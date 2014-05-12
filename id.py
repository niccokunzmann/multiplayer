import os
from threading import Lock
import struct
import bisect

NAME_SIZE = 4

class IDGenerator:

    def __init__(self):
        self._names_to_number = {}
        self._i = 0
        self._name = os.urandom(NAME_SIZE)
        self._id_lock = Lock()

    def get_id(self):
        with self._id_lock:
            try:
                return self._name + struct.pack('<l', self._i)
            finally:
                self._i += 1

    

class IDSet:

    def __init__(self):
        self._names_to_ranges = {} # name : ([starts], [ends])

    def __contains__(self, id):
        name, number = split_id(id)
        start_list, stop_list = self._names_to_ranges.get(name, ((),()))
        if not start_list:
            return False
        index = bisect.bisect(start_list, number)
        if index == len(start_list):
            return not stop_list[-1] <= number
        elif index == 0:
            return not start_list[0] > number
        else:
            return not (start_list[index] > number and stop_list[index - 1] <= number)

    def add(self, id):
        name, number = split_id(id)
        if name not in self._names_to_ranges:
            self._names_to_ranges.setdefault(name, ([], []))
        start_list, stop_list = self._names_to_ranges[name]
        if not start_list:
            start_list.append(number)
            stop_list.append(number + 1)
            return 
        index = bisect.bisect(start_list, number)
        if index == len(start_list):
            if stop_list[-1] == number:
               stop_list[-1] = number + 1
            else:
                assert stop_list[-1] < number, 'use `in` before'
                start_list.append(number)
                stop_list.append(number + 1)
        elif index == 0:
            if start_list[0] == number + 1:
               start_list[0] = number
            else:
                assert stop_list[0] > number, 'I made myself inconsistent. Not your fault.'
                start_list.insert(0, number)
                stop_list.insert(0, number + 1)
        else:
            assert start_list[index] > number, 'use `in` before'
            if start_list[index] == number + 1:
                start_list[index] -= 1
                if stop_list[index - 1] == number:
                    # merge
                    del start_list[index]
                    del stop_list[index - 1]
            elif stop_list[index - 1] < number:
                start_list.insert(index, number)
                stop_list.insert(index, number + 1)
            else:
                assert stop_list[index - 1] == number, 'use `in` before'
                stop_list[index - 1] += 1
                if stop_list[index - 1] == start_list[index]:
                    # merge
                    del start_list[index]
                    del stop_list[index - 1]
                
                
                
                    
                    
            

def split_id(id):
    return id[:NAME_SIZE], struct.unpack('<l', id[NAME_SIZE:])[0]

ID_LENGTH = len(IDGenerator().get_id())

def test(indices):
    ig = IDGenerator()
    id = [ig.get_id() for i in range(100)]
    i = IDSet()
    added = []
    for _i, _id in enumerate(id):
        assert _id not in i, "nothing added, {}".format(split_id(_id)[1])
        assert id.count(_id) == 1
        assert split_id(_id)[1] == _i
    for add_index in indices:
        print('-------------- {}'.format(split_id(id[add_index]))[1])
        added.append(add_index)
        i.add(id[add_index])
        for _i, _id in enumerate(id):
            if _i in added:
                assert _id in i, "{} was added as well as {}".format(_i, added[:-1])
                try:
                    i.add(_id)
                except AssertionError:
                    pass
                else:
                    assert False, "{} was added as well as {}".format(_i, added[:-1])
            else:
                assert _id not in i, "{} was never added. {}".format(_i, added[:-1])
        start, stop = i._names_to_ranges[list(i._names_to_ranges.keys())[0]]
        print(start)
        print(stop)
        
if __name__ == '__main__':
    #test([6, 9, 4, 5, 1, 0, 2, 8, 3, 7])
    # verify
    test([8, 67, 39, 57, 32, 99, 91, 68, 49, 63, 72, 0, 4, 7, 98, 53, 88, 73, 16, 10, 61, 82, 26, 97, 13, 33, 92, 58, 6, 30, 1, 14, 62, 74, 83, 35, 46, 93, 87, 56, 20, 94, 17, 64, 85, 54, 48, 45, 40, 69, 86, 78, 66, 50, 28, 9, 84, 25, 19, 29, 42, 89, 5, 81, 70, 55, 75, 80, 60, 41, 3, 36, 27, 2, 21, 37, 15, 44, 65, 77, 12, 96, 38, 76, 11, 95, 71, 18, 24, 34, 79, 23, 90, 47, 51, 22, 59, 52, 43, 31])
