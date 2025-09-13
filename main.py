import array
import math
from typing import Iterable


class LongNumber:
    __DIGITS__ = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    __type_char__ = 'B'

    def __init__(self, M, N, raw_data=None, sign=False):
        if M < 2 or M > 36:
            raise ValueError("M can not be less than 2 or greater than 36")
        if N < 0:
            raise ValueError("Length of the number N can not be negative")

        self.__M__ = M
        self.__N__ = N
        self.__sign__ = sign
        self.__data__ = array.array(self.__type_char__)

        if raw_data is None:
            raw_data = [0]
        s_type = type(raw_data)

        if s_type == float or s_type == complex:
            raise TypeError(f"Long Number does not support {s_type.__name__} type as a constructor.")

        raw_data = "".join(list(str(i).lower() for i in raw_data)) if issubclass(s_type, Iterable) else str(raw_data)
        result = self._convert_from_decimal(int(raw_data, self.__M__))

        if len(result) > self.__N__:
            raise OverflowError(f"Given number is longer than maximum supported N={self.__N__}")

        sub_data = [0] * self.__N__
        for id_, digit in enumerate(result):
            sub_data[id_] = digit

        self.__data__.fromlist(sub_data)

    def _convert_from_decimal(self, number):
        if number == 0:
            return "0"

        result = []
        while number > 0:
            number, remainder = divmod(number, self.__M__)
            result.append(remainder)

        return result

    def __repr__(self):
        return f"{'-' if self.__sign__ else ''}{''.join(self.__DIGITS__[i] for i in self.__data__[::-1])}"

    def __add__(self, other):
        ...

    def __sub__(self, other):
        ...

    def __mul__(self, other):
        ...

    def __floordiv__(self, other):
        ...


if __name__ == '__main__':
    print(LongNumber(2, 100, "000010101011001"))
    print(LongNumber(10, 10, "123445679"))
    print(LongNumber(16, 100, 0x123abcde))
    print(LongNumber(16, 20, "abcdef"))
