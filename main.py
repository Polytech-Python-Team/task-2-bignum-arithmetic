import array
from typing import Iterable


class LongNumber:
    __type_char__ = 'b'

    def __init__(self, raw_data=None, sign=False):
        self.__sign__ = sign
        self.__data__ = array.array(self.__type_char__)

        if raw_data is None:
            raw_data = [0]
        s_type = type(raw_data)

        if s_type == float or s_type == complex:
            raise TypeError(f"Long Number does not support {s_type} type as a constructor.")

        sub_data = [
            int(i)
            for i in (raw_data if issubclass(s_type, Iterable) else str(raw_data))
        ]
        self.__data__.fromlist(sub_data)

    def __repr__(self):
        return f"{'-' if self.__sign__ else ''}{''.join(str(i) for i in self.__data__)}"

    def __lt__(self, other):
        ...

    def __le__(self, other):
        ...

    def __eq__(self, other):
        ...

    def __add__(self, other):
        ...

    def __sub__(self, other):
        ...

    def __mul__(self, other):
        ...

    def __floordiv__(self, other):
        ...


if __name__ == '__main__':
    print(LongNumber("000010000", True))
    print(LongNumber([0,0,0,0,1, 0, 0, 0, 0]))
    print(LongNumber(10000000))
