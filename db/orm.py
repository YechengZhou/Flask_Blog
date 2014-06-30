#!/usr/bin python
# -*- coding: utf-8 -*-
__author__ = 'Yecheng'
import logging, db, time

class Field(object):

    _count = 0

    def __init__(self, **kw):
        self.name = kw.get('name', None)
        self._default = kw.get('default', None)
        self.primary_key = kw.get('primary_key', False)
        self.nullable = kw.get('nullable', False)
        self.updatable = kw.get('updatable', True)
        self.insertable = kw.get('insertable', True)
        self.ddl = kw.get('ddl', '')
        self._order = Field._count
        Field._count = Field._count + 1

    @property
    def default(self):
        d = self._default
        return d() if callable(d) else d

    def __str__(self):
        s = ['<%s:%s,%s,default(%s),' % (self.__class__.__name__, self.name, self.ddl, self._default)]
        self.nullable and s.append('N')
        self.updatable and s.append('U')
        self.insertable and s.append('I')
        s.append('>')
        return ''.join(s)

class StringField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = ''
        if not 'ddl' in kw:
            kw['ddl'] = 'varchar(255)'
        super(StringField, self).__init__(**kw)

class IntegerField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = 0
        if not 'ddl' in kw:
            kw['ddl'] = 'bigint'
        super(IntegerField, self).__init__(**kw)

class FloatField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = 0.0
        if not 'ddl' in kw:
            kw['ddl'] = 'real'
        super(FloatField, self).__init__(**kw)

class BooleanField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = False
        if not 'ddl' in kw:
            kw['ddl'] = 'bool'
        super(BooleanField, self).__init__(**kw)

class TextField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = ''
        if not 'ddl' in kw:
            kw['ddl'] = 'text'
        super(TextField, self).__init__(**kw)

class BlobField(Field):

    def __init__(self, **kw):
        if not 'default' in kw:
            kw['default'] = ''
        if not 'ddl' in kw:
            kw['ddl'] = 'blob'
        super(BlobField, self).__init__(**kw)

class VersionField(Field):

    def __init__(self, name=None):
        super(VersionField, self).__init__(name=name, default=0, ddl='bigint')

_triggers = frozenset(['pre_insert', 'pre_update', 'pre_delete'])

def _gen_sql(table_name, mappings):
    pk = None
    sql = ['-- generating SQL for %s:' % table_name, 'create table `%s` (' % table_name]
    for f in sorted(mappings.values(), lambda x, y: cmp(x._order, y._order)):
        if not hasattr(f, 'ddl'):
            raise StandardError('no ddl in field "%s".' % f)
        ddl = f.ddl
        nullable = f.nullable
        if f.primary_key:
            pk = f.name
        sql.append(nullable and '  `%s` %s,' % (f.name, ddl) or '  `%s` %s not null,' % (f.name, ddl))
    sql.append('  primary key(`%s`)' % pk)
    sql.append(');')
    real_sql = '\n'.join(sql[1:])
    #logging.info('\n'.join(sql))
    return real_sql

class ModelMetaclass(type):
    '''
    Metaclass for model objects.
    '''
    def __new__(cls, name, bases, attrs):
        # skip base Model class:
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)

        # store all subclasses info:
        if not hasattr(cls, 'subclasses'):
            cls.subclasses = {}
        if not name in cls.subclasses:
            cls.subclasses[name] = name
        else:
            logging.warning('Redefine class: %s' % name)

        logging.info('Scan ORMapping %s...' % name)
        mappings = dict()
        primary_key = None
        for k, v in attrs.iteritems():
            if isinstance(v, Field):
                if not v.name:
                    v.name = k
                logging.info('Found mapping: %s => %s' % (k, v))
                # check duplicate primary key:
                if v.primary_key:
                    if primary_key:
                        raise TypeError('Cannot define more than 1 primary key in class: %s' % name)
                    if v.updatable:
                        logging.warning('NOTE: change primary key to non-updatable.')
                        v.updatable = False
                    if v.nullable:
                        logging.warning('NOTE: change primary key to non-nullable.')
                        v.nullable = False
                    primary_key = v
                mappings[k] = v
        # check exist of primary key:
        if not primary_key:
            raise TypeError('Primary key not defined in class: %s' % name)
        for k in mappings.iterkeys():
            attrs.pop(k)
        if not '__table__' in attrs:
            attrs['__table__'] = name.lower()
        attrs['__mappings__'] = mappings
        attrs['__primary_key__'] = primary_key
        attrs['__sql__'] = lambda self: _gen_sql(attrs['__table__'], mappings)
        for trigger in _triggers:
            if not trigger in attrs:
                attrs[trigger] = None
        return type.__new__(cls, name, bases, attrs)


class Model(dict):
    __metaclass__ = ModelMetaclass

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(r"'Model' has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        self[key] = value

    @classmethod
    def get(cls,pk):
        """
        get from primary key
        @param pk:
        @return:
        """
        d = db.select_first_one('select * from %s where %s=?' % (cls.__table__, cls.__primary_key__.name), pk)
        return cls(**d) if d else None

    @classmethod
    def find_first(cls, where, *args):
        """
        First one returned, if no result return None
        @param where: clause
        @param args: options
        @return: first one result, if no result, None
        """
        d = db.select_first_one("select * from %s %s" % (cls.__table__, where), *args)
        return cls(**d) if d else None

    @classmethod
    def find_all(cls, *args):
        """
        find all and return a result list
        @param args:
        @return:
        """
        l = db.select("select * from %s" % cls.__table__)
        return [cls(**d) for d in l]

    @classmethod
    def find_by(cls, where, *args):
        """
        return a result list by where options
        @param where:
        @param args:
        @return:
        """
        l = db.select("select * from %s %s" % (cls.__table__, where), *args)
        return [cls(**d) for d in l]

    @classmethod
    def count_all(cls):
        """
        select count(pk) from table,
        @return: integer
        """
        return db.select('select count(%s) from %s' % (cls.__primary_key__.name, cls.___table__))

    @classmethod
    def count_by(cls, where, *args):
        """
        select count(pk) from table where...
        @param where:
        @param args:
        @return:
        """
        return db.select('select count(%s) from %s %s' % (cls.__primary_key__.name, cls.___table__), *args)

    @classmethod
    def save(cls):
        """
        Create table for a Model class

        sql = "insert into %s (%s) values (%s)"
        columns = []
        paras = []
        values = []
        for k,v in cls.__mapping__.iteritems():
            columns.append(v.name)
            paras.append('?')
            values.append(getattr(self, k, None))
        sql = sql % (cls.__table__, ','.join(columns), ','.join(paras))
        logging.info("SQL: %s" % sql)
        logging.info("Values: %s" % values)
         """
        logging.info("Creating table %s" % str(cls.__name__))
        try:
            db.update(cls().__sql__())
        except BaseException,e:
            if e.msg.__contains__('already exists'):
                logging.warn(e.msg)
            else:
                raise e

        #print cls.__sql__

    def insert(self):  # a little similar with save
        paras = {}
        for k, v in self.__mappings__.iteritems():
            if v.insertable:
                if not hasattr(self, k):
                    setattr(self, k, v.default)
                paras[v.name] = getattr(self, k)
        db.insert(str(self.__table__), **paras)
        return self

    def delete(self):
        pk = self.__primary_key__.name
        args = (getattr(self, pk), )
        db.update('delete from `%s` where `%s`=?' % (self.__table__, pk), *args)
        return self

    def update(self):
        self.pre_update and self.pre_update()
        L = []
        args = []
        for k, v in self.__mappings__.iteritems():
            if v.updatable:
                if hasattr(self, k):
                    arg = getattr(self, k)
                else:
                    arg = v.default
                    setattr(self, k, arg)
                L.append('`%s`=?' % k)
                args.append(arg)
        pk = self.__primary_key__.name
        args.append(getattr(self, pk))
        db.update('update `%s` set %s where %s=?' % (self.__table__, ','.join(L), pk), *args)
        return self

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db.create_engine(user="root", password="", database='test')
    class User(Model):
        id = IntegerField(primary_key=True)
        name = StringField()
        email = StringField(updatable=False)
        passwd = StringField(default=lambda: '******')
        last_modified = FloatField()
        def pre_insert(self):
            self.last_modified = time.time()
    User.save()
    # 创建一个实例：
    u = User(id=12345, name='ethan', email='test@123.com', password='pwd')
    # 保存到数据库：
    u.insert()