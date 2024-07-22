from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod

class FIFO(ABC):
    _size: int = 0
    _overlap: bool = False

    @abstractmethod
    def __init__(self, size: int, overlap: bool) -> None:
        """ Create cycle FIFO

        Args:
            size (int): size of buffer
            overlap (bool): flag if overlapping is allowed when buffer is full
        """
        if size < 0:
            raise ValueError("Size cannot be less than 1!")

        self._size = size
        self._overlap = overlap

    @abstractmethod
    def isFull(self) -> bool:
        """ Check if FIFO is full

        Returns:
            bool: status if FIFO is full
        """

    @abstractmethod
    def isEmpty(self) -> bool:
        """ Check if FIFO is empty

        Returns:
            bool: True if there is no any values to read, False otherwise
        """

    @abstractmethod
    def write(self, value: Any) -> bool:
        """ Write value to FIFO if it's possible

        Args:
            value (Any): value to write in FIFO

        Returns:
            bool: True if value was added to FIFO.
                  False if it is full and overlap is disable
        """

    @abstractmethod
    def read(self) -> Any | None:
        """ Reads value from FIFO

        Returns:
            Any | None: value or None if FIFO is empty
        """

    @abstractmethod
    def clear(self) -> None:
        """ Clear the FIFO
        """

class FirstFIFO(FIFO):
    """
    FIFO using list (array)

    Работа основывается на массиве и индексах для чтения/записи, так что затрачивается
        время на вычисление индексов после операций.
    Затрачивает меньше памяти нежели вариант для связного списка
    """
    _data: list[Any] = None
    _read_count = 0
    _read_index = 0
    _write_count = 0
    _write_index = 0

    def __init__(self, size: int, overlap: bool) -> None:
        super().__init__(size, overlap)
        self._data = [None for _ in range(size)]

    def isFull(self) -> bool:
        return (
            self._write_count > self._read_count
            and
            self._write_index == self._read_index
        )

    def isEmpty(self) -> bool:
        return self._read_count == self._write_count

    def write(self, value: Any) -> bool:
        is_full = self.isFull()
        if not self._overlap and is_full:
            return False

        if self._overlap and is_full:
            self._read_count += 1
            self._read_index = self._read_count % self._size

        self._data[self._write_index] = value
        self._write_count += 1
        self._write_index = self._write_count % self._size
        return True

    def read(self) -> Any | None:
        if self.isEmpty():
            return None

        value = self._data[self._read_index]
        self._data[self._read_index] = None
        self._read_count += 1
        self._read_index = self._read_count % self._size
        return value

    def clear(self) -> None:
        self._read_count = 0
        self._write_count = 0
        self._read_index = 0
        self._write_index = 0
        self._data.clear()

class LinkedNode():
    _value: Any = None
    _next: LinkedNode = None

    def __init__(self, value: Any, next: LinkedNode | None = None) -> None:
        self._value = value
        self._next = next

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._value = value

    @property
    def next(self) -> Any:
        return self._next

    @next.setter
    def next(self, next: LinkedNode) -> None:
        self._next = next

class LinkedFIFO(FIFO):
    """
    FIFO using cycled linked list

    Работа строится на указателях, так что не тратится время на арифметику.
    Требует больше памяти, нежели реализация через массив, за счет хранения указателя
        на следующий элемент.
    """
    _head: LinkedNode = None
    _end: LinkedNode = None

    _read_ptr: LinkedNode = None
    _write_ptr: LinkedNode = None

    _read_count = 0
    _write_count = 0

    def __init__(self, size: int, overlap: bool) -> None:
        super().__init__(size, overlap)
        self._head = LinkedNode(None)
        ptr = self._head
        for _ in range(1, size):
            ptr.next = LinkedNode(None)
            ptr = ptr.next

        ptr.next = self._head
        self._end = ptr

        self._read_ptr = self._head
        self._write_ptr = self._head

    def isFull(self) -> bool:
        return (
            self._read_ptr == self._write_ptr
            and
            self._read_count <= self._write_count
        )

    def isEmpty(self) -> bool:
        return self._read_count == self._write_count

    def write(self, value: Any) -> bool:
        is_full = self.isFull()
        if not self._overlap and is_full:
            return False

        if self._overlap and is_full:
            self._read_ptr = self._read_ptr.next

        self._write_ptr.value = value
        self._write_ptr = self._write_ptr.next
        return True

    def read(self) -> Any | None:
        if self.isEmpty():
            return None

        value = self._read_ptr.value
        self._read_ptr.value = None
        self._read_ptr = self._read_ptr.next
        return value

    def clear(self) -> None:
        self._head.value = None
        ptr: LinkedNode = self._head.next
        while ptr != self._head:
            ptr.value = None
            ptr = ptr.next

        self._read_ptr = self._head
        self._write_ptr = self._head
