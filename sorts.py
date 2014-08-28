__author__ = 'yechengzhou'

def bubble(l):
    length = len(l)
    for i in range(length):
        for j in range(i+1, length):
            if l[i] > l[j]:
                l[i], l[j] = l[j], l[i]
    print l


def select(l):
    length = len(l)
    for i in range(length):
        minn = i
        for j in range(i+1, length):
            if l[j] < l[minn]:
                minn = j
        l[i], l[minn] = l[minn], l[i]
    print l


def insert(l):
    length = len(l)
    for i in range(1,length):
        key = l[i]
        j = i - 1
        while j > 0 and l[j] > key:
            l[j+1] = l[j]
            j -= 1
        l[j+1] = key
    print l


def quick(l, left, right):
    if left < right:
        pivot = partition(l, left, right)
        quick(l, left, pivot - 1)
        quick(l, pivot + 1, right)


def partition(l, left, right):
    pivot = l[left]
    i, j = left, right
    while i < j:
        while i < j and l[j] >= pivot:
            j -= 1
        if i < j:
            l[i] = l[j]
            i += 1
        while i < j and l[i] <= pivot:
            i += 1
        if i < j:
            l[j] = l[i]
            j -= 1
    l[i] = pivot
    return i


def quick_simple(l):
    if len(l) > 1:
        return quick_simple( [i for i in l[1:] if i < l[0]] ) + l[0:1] + quick_simple( [j for j in l[1:] if j >= l[0]] )
    else:
        return l


l = [4,3,2,1,5,7,9,8]
#bubble(l[:])
#select(l[:])
#insert(l[:])
#quick(l[:])

#quick(l, 0, len(l)-1)
#print l

print quick_simple(l)

#partition([1, 3, 2, 4, 5, 7, 9, 8],0,7)