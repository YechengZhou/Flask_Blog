#!/usr/bin python
# -*- coding: utf-8 -*-
__author__ = 'yechengzhou'

import threading, logging, time, uuid, functools


"""
db operation module
"""


class MyDict(dict):
    def __init__(self,name=(),values=(),**kw):
        super(MyDict,self).__init__(**kw)
        for k,v in zip(name,values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'MyDict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


# define some customized error for db module
class DBError(BaseException):
    pass


class MultiColumnsError(DBError):
    pass


def next_id(t=None):
    """
    Return next id as 50-char string.

    Args:
        t: unix timestamp, default to None and using time.time().
    """
    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def _profiling(start,sql = ''):  # decorator function
    t = time.time() - start
    if t > 0.1 :
        logging.warning('[Profiling] [DB] {}:{}'.format(t, sql))
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


# 数据库引擎类
class _Engine(object):

    def __init__(self,connect):
        self._connect = connect

    def connect(self):
        return self._connect()  # 返回一个数据库连接实例

engine = None


def create_engine(user, password, database, host = "127.0.0.1", port = 3306, **kwargs):

    global engine
    if engine is not None:
        raise DBError()
    import mysql.connector
    config = {
        'host': host,
        'user': user,
        "password": password,
        'port': port,
        'database': database,
        'charset': 'utf8',   # 默认使用utf8
        'use_unicode': True,
        'charset': 'utf8',
        'collation': 'utf8_general_ci',
        'autocommit': False
    }

    for k,v in kwargs:
        config[k] = v
    """
    try:
        conn = mysql.connector.connect( **config )
    except mysql.connector.Error as e:
        logging.info("connection error<{}>".format(str(e)))
        raise e
    """
    engine = _Engine(lambda: mysql.connector.connect(**config))
    logging.info("Init mysql engine <%s> ok." % hex(id(engine)))

# 持有数据库连接的上下文类
class _DBCtx(threading.local): # 对于每个线程 都是不一样的

    def __init__(self):
        self.connection = None
        self.transactions = 0

    def is_init(self):
        return not self.connection is None

    def init(self):
        logging.info('open lazy connection...')
        self.connection = _LazyConnection()
        self.transactions = 0  # 事务计数器

    def cleanup(self):
        self.connection.cleanup()
        self.connection = None

    def cursor(self):
        return self.connection.cursor()

_db_ctx = _DBCtx()

class _ConnectionCtx(object):
    '''
    _ConnectionCtx object that can open and close connection context. _ConnectionCtx object can be nested and only the most 
    outer connection has effect.
    '''
    def __enter__(self):
        global _db_ctx
        self.should_cleanup = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        global _db_ctx
        if self.should_cleanup:
            _db_ctx.cleanup()


class _LazyConnection(object):

    def __init__(self):
        self.connection = None

    def cursor(self):
        if self.connection is None:
            this_connection = engine.connect()
            logging.info('open connection <%s>...' % hex(id(this_connection)))
            self.connection = this_connection
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def cleanup(self):
        if self.connection:
            connection = self.connection
            self.connection = None
            logging.info('close connection <%s>...' % hex(id(connection)))
            connection.close()


def connection():
    return _ConnectionCtx()

def with_connection(func):
    """
    decorator to ensure connection is ready when do db operations
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        with _ConnectionCtx():
            return func(*args, **kw)
    return _wrapper


class _TransactionTCtx(object):

    def __enter__(self):
        global _db_ctx
        self.should_close_connection = False
        if not _db_ctx.is_init():
            _db_ctx.init()
            self.should_close_connection = True
        _db_ctx.transactions += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _db_ctx
        _db_ctx.transactions -= 1
        try:
            if _db_ctx.transactions == 0:
                if exc_type is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_connection:
                _db_ctx.cleanup()

    def commit(self):
        global _db_ctx
        try:
            _db_ctx.connection.commit()
        except:
            _db_ctx.connection.rollback()
            raise

    def rollback(self):
        global _db_ctx
        _db_ctx.connection.rollback()


def transaction():
    """
    return a _TransactionTCtx
    with transaction():
        pass
    """
    return _TransactionTCtx()


def with_transaction(func):
    """
    decorator for transaction, return a function
    """
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        tt = time.time()
        with _TransactionTCtx():
            return func(*args, **kw)
        _profiling(tt)
    return _wrapper


def with_sql_logging(func):
    """
    decorator to help sql operation function to print logs
    """
    #sql, arg = func.func_code.co_names
    #sql = sql.replace("?", "%s")
    #logging.info("SQL: %s, ARGS: %s" % (sql, arg))
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        arg_counts = func.func_code.co_argcount
        args = func.func_code.co_varnames[0:arg_counts]
        template = "%s have %s arguments:" + "%s "*arg_counts
        logging.info(template % tuple([func.__name__, arg_counts] + list(args)))
        return func(*args, **kwargs)
    return _wrapper()


# db operations
"""
users = db.select('select * from user')
# users =>
# [
#     { "id": 1, "name": "Michael"},
#     { "id": 2, "name": "Bob"},
#     { "id": 3, "name": "Adam"}
# ]
"""


#@with_sql_logging
def _select(sql, need_first, *args):
    # execute select sql and return result likes below
    global _db_ctx
    this_cursor = None
    sql = sql.replace("?","%s")
    logging.info("SQL: %s, ARGS: %s" % (sql, args))  # select ?,? from ? where ? = ?
    try:
        this_cursor = _db_ctx.connection.cursor()
        this_cursor.execute(sql, args)  # support value=[1,'hi rollen'] cur.execute('insert into test values(%s,%s)',value)
        columns = []
        if this_cursor.description:
            columns = [i[0] for i in this_cursor.description]
        if need_first:
            values = this_cursor.fetchone()
            if not values:
                return None
            else:
                return MyDict(columns, values)
                # generate result list
        else:
            return [MyDict(columns, i) for i in this_cursor.fetchall()]
    finally:
        if this_cursor:
            this_cursor.close()

@with_connection
def select_first_one(sql, *args):
    """
    select first item from the fetch result
    if nothing returned, return None
    @param sql: sql which need to execute
    @param args: replacement of ?
    @return:
    """
    return _select(sql, True, *args)

@with_connection
def select(sql, *args):
    """
    just like other
    @param sql:
    @return:
    """
    return _select(sql, False, *args)

@with_connection
def execute(sql):
    """
    execute special sqls like show/...
    @param sql:
    @return:
    """
    global _db_ctx
    logging.info("SQL: %s" % sql)
    this_cursor = None
    try:
        this_cursor = _db_ctx.connection.cursor()
        this_cursor.execute(sql)

    finally:
        print this_cursor.description

#@with_sql_logging
def _update(sql, *args):
    """
    n = db.update('insert into user(id, name) values(?, ?)', 4, 'Jack')
    @param sql:
    @param args:
    @return: affected rows
    """
    global _db_ctx
    this_cursor = None
    sql = sql.replace("?", "%s")
    logging.info("SQL: %s, ARGS: %s" % (sql, args))
    try:
        print _db_ctx.connection
        this_cursor = _db_ctx.connection.cursor()
        this_cursor.execute(sql, args)
        r = this_cursor.rowcount
        if _db_ctx.transactions == 0:
            logging.info('auto commit')
            _db_ctx.connection.commit()
        return r
    finally:
        if this_cursor:
            this_cursor.close()

@with_connection
def insert(table,**kwargs):
    """
    insert to table
    insert(user,**args)  id = 1, name = 'ethan'
    @param table:
    @return:
    """
    cols, args = zip(*kwargs.iteritems())
    print cols, args
    sql = 'insert into `%s` (%s) values (%s)' % (table, ','.join([col for col in cols]), ','.join(['?' for i in range(len(cols))]))
    return _update(sql, *args)

@with_connection
def update(sql, *args):
    return _update(sql, *args)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    create_engine(user="root", password="", database='test')
    update('drop table if exists user;')
    update('create table user (id int primary key, name text, email text, passwd text, last_modified real)')
    insert('user',id=0,name="ethan",passwd='123')
    insert('user',id=1,name="ethan",passwd='1234')
    print select('select * from user where name = ?','ethan')  # table name can not use format
    import doctest
    doctest.testmod()