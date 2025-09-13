import array
import copy
import math
from typing import Iterable

REPR_LONGNUMBER_LENGTH = 25


class LongNumber:
    __type_char__ = 'B'
    __type_char_equiv__ = ('B', 'H', 'L', 'Q')

    @property
    def M(self):
        return self.__M__

    @property
    def N(self):
        return self.__N__

    @property
    def sign(self):
        return self.__sign__

    def __init__(self, M, N, raw_data=None, sign=False):
        """
        :param M: base
        :param N: maximum number size
        :param raw_data: data in base 10, ONLY POSITIVE. EXCLUDING types with floating point
        :param sign: is it negative or not
        """

        if N < 0:
            raise ValueError("Length of the number N can not be negative")

        self.__M__ = M
        type_char_id = math.log2(math.ceil(math.log2(self.__M__) / 8))
        self.__type_char__ = self.__type_char_equiv__[math.ceil(type_char_id)]

        self.__N__ = N
        self.__sign__ = sign
        self.__data__ = array.array(self.__type_char__)

        if raw_data is None:
            raw_data = [0]

        if isinstance(raw_data, array.array):
            self.__data__ = copy.copy(raw_data)
            self.__type_char__ = self.__data__.typecode
            return

        raw_data_type = type(raw_data)
        if isinstance(raw_data, float) or isinstance(raw_data, complex):
            raise TypeError(f"Long Number does not support {raw_data_type.__name__} type as a constructor.")

        raw_data = "".join(map(str, raw_data)) if issubclass(raw_data_type, Iterable) else str(raw_data)
        for digit in raw_data:
            if not digit.isdigit():
                raw_data = raw_data.replace(digit, '')

        raw_data = raw_data.strip()
        result = self._convert_from_decimal(int(raw_data))

        if len(result) > self.N:
            raise OverflowError(f"Given number is longer than maximum supported N={self.N}")

        self.__data__.fromlist(result)

    def _convert_from_decimal(self, number):
        if number == 0:
            return "0"

        result = []
        while number > 0:
            number, remainder = divmod(number, self.M)
            result.append(remainder)

        return result

    def __repr__(self):
        obfuscate = '' if self.N <= REPR_LONGNUMBER_LENGTH else '<...> |'
        repr_size = min(REPR_LONGNUMBER_LENGTH, self.N)
        data_part = [str(i) for i in self.__data__[::-1][:repr_size]]
        return f"{'-' if self.__sign__ else ''}{obfuscate}{'0|' * (repr_size - len(data_part))}{'|'.join(data_part)}"

    def __add__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        if self.sign != other.sign:
            abs_self = abs(self)
            abs_other = abs(other)

            if self.sign:
                return abs_other - abs_self
            return abs_self - abs_other

        result = array.array(self.__type_char__)
        result_sign = self.sign

        carry = 0
        max_len = max(len(self.__data__), len(other.__data__))
        for i in range(max_len):
            self_digit = self.__data__[i] if i < len(self.__data__) else 0
            other_digit = other.__data__[i] if i < len(other.__data__) else 0
            total = self_digit + other_digit + carry
            carry = total // self.M
            result.append(total % self.M)

        result.append(carry)

        len_res = len(result)
        result_N = max(self.N, other.N)
        if len_res > result_N:
            raise OverflowError(f'Result is too big to fit in the given size: {len_res} > {result_N}')

        return LongNumber(self.M, result_N, result, result_sign)

    def __sub__(self, other):
        ...

    def __mul__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        result_N = max(self.N, other.N)
        result_data_len = len(self.__data__) + len(other.__data__)
        if result_data_len > result_N:
            raise OverflowError(
                f'Multiplication resulted in overflow. '
                f'Result length is {result_data_len} greater than standard N={result_N}'
            )

        result = array.array(self.__type_char__, [0] * max(self.N, result_N))

        for i, self_digit in enumerate(self.__data__):
            carry = 0
            for j, other_digit in enumerate(other.__data__):
                product = self_digit * other_digit + result[i + j] + carry
                carry = product // self.M
                result[i + j] = product % self.M
            if carry:
                result[i + len(other.__data__)] += carry

        return LongNumber(self.M, result_N, result, self.__sign__ != other.__sign__)

    def __floordiv__(self, other):
        ...

    def __abs__(self):
        return LongNumber(self.M, self.N, self.__data__)


if __name__ == '__main__':
    print(LongNumber(2, 100, "00001032429374239467293847101011001"))
    print(LongNumber(10, 10, "123445679"))
    print(LongNumber(16, 100, 0x123abcde))
    print(LongNumber(16, 20, "283764827364"))
    print(LongNumber(10 ** 3, 10 ** 9, "324948756348576348658346532674872364"))
    print(LongNumber(10, 10, array.array('H', [1, 2, 3, 4, 5])))

    print()
    print(f"{'=' * 10} Math Operations {'=' * 10}")
    print()

    a = LongNumber(100, 2, 9999, True)
    b = LongNumber(100, 3, 9999, True)

    print(a, '+', b, ' = ', a + b)

    c = LongNumber(10, 5, 999)
    d = LongNumber(10, 5, 99)

    print(c, ' * ', d, ' = ', c * d)
