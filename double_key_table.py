from __future__ import annotations

from typing import Generic, TypeVar, Iterator
from data_structures.hash_table import LinearProbeTable, FullError
from data_structures.referential_array import ArrayR

K1 = TypeVar('K1')
K2 = TypeVar('K2')
V = TypeVar('V')

class K1K2LinkList(Iterator[K1|K2]):
    '''A list only designed for search K1/K2 type'''

    def __init__ (self, table : DoubleKeyTable , key : K1|None = None) -> None :
        self.table = table
        self.iterated_key = key
        self.index_position = 0

    def __iter__(self) -> Iterator[K1|K2]:
        return self

    def __next__(self) -> K1|K2:

        if self.iterated_key == None:
            temp_key = self.find_key(self.table.array)
            if temp_key != None:
                return temp_key
            raise StopIteration
        
        else:
            inner_table = None
            for item in self.table.array:
                if item != None:
                    key_item, inner_table_item = item
                    if self.iterated_key == key_item:
                        inner_table = inner_table_item
            if inner_table != None:
                temp_key = self.find_key(inner_table.array)
                if temp_key != None:
                    return temp_key
            raise StopIteration


    def find_key(self, array : ArrayR) -> K1|K2:


        for _ in range (self.index_position, len(array)):

            if array[self.index_position] != None:
                key_item = array[self.index_position][0]
                self.index_position += 1
                return key_item

            self.index_position += 1

        return None
class VLinkList(Iterator[V]):

    def __init__ (self, table : DoubleKeyTable , key : K1|None = None) -> None :



        self.table = table
        self.iterated_key = key
        self.index_position = 0
        self.inner_index_position = 0

    def __iter__(self) -> Iterator[V]:


        return self

    def __next__(self) -> V:

        if self.iterated_key == None:

            for _ in range (self.index_position, len(self.table.array)):
                if self.table.array[self.index_position] != None:
                    inner_table = self.table.array[self.index_position][1]

                    temp_value = self.find_value(inner_table.array)
                    if temp_value != None:
                        return temp_value
                        
                self.index_position += 1
                self.inner_index_position = 0
            
        else:
            inner_table = None

            for item in self.table.array:
                if item != None:
                    if self.iterated_key == item[0]:
                        inner_table = item[1]

            if inner_table != None:
                temp_value = self.find_value(inner_table.array)
                if temp_value != None:
                    return temp_value

        raise StopIteration


    def find_value(self, array : ArrayR) -> V:

        for _ in range (self.inner_index_position, len(array)):
            if array[self.inner_index_position] != None:
                value_item = array[self.inner_index_position][1]
                self.inner_index_position += 1
                return value_item
                
            self.inner_index_position += 1
        
        return None

class DoubleKeyTable(Generic[K1, K2, V]):
    """
    Double Hash Table.

    Type Arguments:
        - K1:   1st Key Type. In most cases should be string.
                Otherwise `hash1` should be overwritten.
        - K2:   2nd Key Type. In most cases should be string.
                Otherwise `hash2` should be overwritten.
        - V:    Value Type.

    Unless stated otherwise, all methods have O(1) complexity.
    """

    # No test case should exceed 1 million entries.
    TABLE_SIZES = [5, 13, 29, 53, 97, 193, 389, 769, 1543, 3079, 6151, 12289, 24593, 49157, 98317, 196613, 393241, 786433, 1572869]

    HASH_BASE = 31

    def __init__(self, sizes: list | None = None, internal_sizes: list | None = None) -> None:
        if sizes is not None:
            self.TABLE_SIZES = sizes

        if internal_sizes is not None:
            self.internal_sizes = internal_sizes
        else:
            self.internal_sizes = self.TABLE_SIZES

        self.size_index = 0
        self.array: ArrayR[tuple[K1, V] | None] | None = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0

    def hash1(self, key: K1) -> int:
        """
        Hash the 1st key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % self.table_size
            a = a * self.HASH_BASE % (self.table_size - 1)
        return value

    def hash2(self, key: K2, sub_table: LinearProbeTable[K2, V]) -> int:
        """
        Hash the 2nd key for insert/retrieve/update into the hashtable.

        :complexity: O(len(key))
        """

        value = 0
        a = 31417
        for char in key:
            value = (ord(char) + a * value) % sub_table.table_size
            a = a * self.HASH_BASE % (sub_table.table_size - 1)
        return value

    def _linear_probe(self, key1: K1, key2: K2 | None, is_insert: bool) -> tuple[int, int] | int:
        """
        Find the correct position for this key in the hash table using linear probing.

        :raises KeyError: When the key pair is not in the table, but is_insert is False.
        :raises FullError: When a table is full and cannot be inserted.
        """

        position1 = self.hash1(key1)
        position2 = -1
        for i in range(self.table_size):
            if self.array[position1] is None:
                if is_insert:
                    if key2 != None:
                        sub_table : LinearProbeTable[K2 , V] =  LinearProbeTable(sizes = self.internal_sizes)
                        sub_table.hash = lambda k: self.hash2(k, sub_table)
                        self.array[position1] = (key1, sub_table)  
                        position2 = sub_table._linear_probe(key2, is_insert)

                    self.count += 1    
                    return (position1, position2)

                raise KeyError(key1) #else if is_insert is false

            elif self.array[position1][0] == key1:
                sub_table = self.array[position1][1]
                position2 = sub_table._linear_probe(key = key2 , is_insert = is_insert)
                return (position1 , position2)
                
            
            position1 = (position1 + 1) % (self.table_size) # else search for the key empty slot

        if is_insert:
            raise FullError("Table is full!")
        
        raise KeyError(key1) # else if is_insert is false and key1 is not present in the hash table



    def iter_keys(self, key: K1 | None = None) -> Iterator[K1 | K2]:
        """
        key = None:
            Returns an iterator of all top-level keys in hash table
        key = k:
            Returns an iterator of all keys in the bottom-hash-table for k.
        """
        return K1K2LinkList(self, key) 


    def iter_values(self, key: K1 | None = None) -> Iterator[V]:
        """
        key = None:
            Returns an iterator of all values in hash table
        key = k:
            Returns an iterator of all values in the bottom-hash-table for k.
        """

        return VLinkList(self, key) 

    def keys(self, key: K1 | None = None) -> list[K1 | K2]:
        """
        key = None: returns all top-level keys in the table.
        key = x: returns all bottom-level keys for top-level key x.
        """
        if key == None:
            keylist = []
            for row in self.array:
                if row != None:
                    keylist.append(row[0])
            return keylist 
        
        for row in self.array:
            if row != None and row[0] == key:
                sub_table = row[1]
                return sub_table.keys()
    

    def values(self, key: K1 | None = None) -> list[V]:
        """
        key = None: returns all values in the table.
        key = x: returns all values for top-level key x.
        """
        valuelist=[]
        if key == None:
            for row in self.array:
                if row != None:
                    sub_table = row[1]
                    valuelist.extend(sub_table.values())                        
        else:
            for row in self.array:
                if row != None:  
                    curKey, sub_table = row
                    if curKey == key:
                        return sub_table.values()

        return valuelist

    def __contains__(self, key: tuple[K1, K2]) -> bool:
        """
        Checks to see if the given key is in the Hash Table

        :complexity: See linear probe.
        """
        try:
            _ = self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key: tuple[K1, K2]) -> V:
        """
        Get the value at a certain key

        :raises KeyError: when the key doesn't exist.
        """

        position1, position2 = self._linear_probe(key[0], key[1], False)
        return self.array[position1][1].array[position2][1]

    def __setitem__(self, key: tuple[K1, K2], data: V) -> None:
        """
        Set an (key, value) pair in our hash table.
        """

        position1, _ = self._linear_probe(key1 = key[0], key2 = key[1], is_insert = True)
        inner_table : LinearProbeTable[K2,V] = self.array[position1][1]
        inner_table[key[1]] = data

        if len(self) > self.table_size / 2:
            self._rehash()

    def __delitem__(self, key: tuple[K1, K2]) -> None:
        """
        Deletes a (key, value) pair in our hash table.

        :raises KeyError: when the key doesn't exist.
        """
        position1, _ = self._linear_probe(key[0], key[1], False)
        sub_table = self.array[position1][1]
        del sub_table[key[1]]

        if len(sub_table) == 0:
            self.array[position1] = None
            self.count -= 1

            position1 = (position1 + 1) % self.table_size

            while self.array[position1] != None:

                keyCur, value = self.array[position1]

                new_position1, _ = self._linear_probe(key1 = keyCur, key2 = None, is_insert = True)
                self.array[position1] = None
                self.array[new_position1] = (keyCur, value)
                
                position1 = (position1 + 1) % self.table_size

 

    def _rehash(self) -> None:
        """
        Need to resize table and reinsert all values

        :complexity best: O(N*hash(K)) No probing.
        :complexity worst: O(N*hash(K) + N^2*comp(K)) Lots of probing.
        Where N is len(self)
        """
        old_array = self.array
        self.size_index += 1 

        if self.size_index >= len(self.TABLE_SIZES):
            return
        
        self.array : ArrayR[tuple[K1, LinearProbeTable[K2, V]]] = ArrayR(self.TABLE_SIZES[self.size_index])
        self.count = 0 

        if old_array == None:
            return
        
        for row in old_array:
            if row != None:
                top_key, sub_table = row
                new_index_1, new_index_2 = self._linear_probe(top_key, None, True)
                self.array[new_index_1] = (top_key, sub_table)


    @property
    def table_size(self) -> int:
        """
        Return the current size of the table (different from the length)
        """
        return len(self.array)

    def __len__(self) -> int:
        """
        Returns number of elements in the hash table
        """
        return self.count

    def __str__(self) -> str:
        """
        String representation.

        Not required but may be a good testing tool.
        """
        result = str()
        for k1, sub_table in self.array:
            if sub_table != None:
                for k2, v in sub_table:
                    result += str (k1) + str(k2) + str(v) + str("\n")
        return result





        