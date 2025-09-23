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
            return [0]

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

        if carry > 0:
            result.append(carry)

        len_res = len(result)
        result_N = max(self.N, other.N)
        if len_res > result_N:
            raise OverflowError(
                f'Addition resulted in overflow. \n'
                f'Result is too big to fit in the given size: {len_res} > {result_N}'
            )

        return LongNumber(self.M, result_N, result, result_sign)

    def __sub__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        if self.sign != other.sign:
            new_other = LongNumber(other.M, other.N, other.__data__, sign=self.sign)

            return self + new_other

        if self.sign:
            abs_self = abs(self)
            abs_other = abs(other)

            return abs_other - abs_self

        cmp  = self._compare_abs(other)

        if cmp == 0:
            return LongNumber(self.M, max(self.N, other.N), 0)

        first_number = self.__data__ if cmp > 0 else other.__data__
        second_number = other.__data__ if cmp > 0 else self.__data__
        result_sign = False if cmp > 0 else True

        result = array.array(self.__type_char__)

        carry = 0
        max_len = max(len(self.__data__), len(other.__data__))
        for i in range(max_len):
            self_digit = first_number[i] - carry if i < len(first_number) else 0
            other_digit = second_number[i] if i < len(second_number) else 0

            if self_digit < other_digit:
                result.append(self.M - (other_digit - self_digit))
                carry = 1

            else:
                result.append(self_digit - other_digit)
                carry = 0

        len_res = len(result)
        result_N = max(self.N, other.N)
        if len_res > result_N:
            raise OverflowError(
                f'Subtraction resulted in overflow. \n'
                f'Result is too big to fit in the given size: {len_res} > {result_N}'
            )

        return LongNumber(self.M, result_N, result, result_sign)

    def __mul__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        result_N = max(self.N, other.N)
        result_data_len = len(self.__data__) + len(other.__data__)
        if result_data_len - 1 > result_N:
            raise OverflowError(
                f'Multiplication resulted in overflow. \n'
                f'Result is too big to fit in the given size: {result_data_len} or {result_data_len - 1} > {result_N}'
            )

        result = array.array(self.__type_char__, [0] * max(self.N, result_N))

        for i, self_digit in enumerate(self.__data__):
            carry = 0
            for j, other_digit in enumerate(other.__data__):
                product = self_digit * other_digit + result[i + j] + carry
                carry = product // self.M
                result[i + j] = product % self.M
            if carry:
                try:
                    result[i + len(other.__data__)] += carry
                except IndexError:
                    raise OverflowError(
                        f'Multiplication resulted in overflow. \n'
                        f'Result is too big to fit in the given size: {result_data_len} > {result_N}'
                    )

        return LongNumber(self.M, result_N, result, self.__sign__ != other.__sign__)

    def __floordiv__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        if other == LongNumber(other.M, other.N, 0):
            raise ZeroDivisionError("Division by zero")

        if self == LongNumber(self.M, self.N, 0):
            return LongNumber(self.M, max(self.N, other.N), 0)

        if other == LongNumber(other.M, other.N, [1]):
            return LongNumber(self.M, self.N, self.__data__, self.sign != other.sign)

        abs_self = abs(self)
        abs_other = abs(other)

        if abs_self < abs_other:
            return LongNumber(self.M, max(self.N, other.N), 0)

        return self._knuth_division(abs_other)

    def _knuth_division(self, divisor):
        n = len(divisor.__data__)
        m = len(self.__data__) - n

        d = self.M // (divisor.__data__[-1] + 1)

        u = self * LongNumber(self.M, len(self.__data__) + 1, [d])
        v = divisor * LongNumber(divisor.M, len(divisor.__data__), [d])

        q = array.array(self.__type_char__, [0] * (m + 1))

        for j in range(m, -1, -1):
            u_jn = u.__data__[j + n] * self.M + u.__data__[j + n - 1]
            v_n1 = v.__data__[n - 1]

            q_hat = u_jn // v_n1
            r_hat = u_jn % v_n1

            while q_hat == self.M or (q_hat * v.__data__[n - 2] > self.M * r_hat + u.__data__[j + n - 2]):
                q_hat -= 1
                r_hat += v_n1
                if r_hat >= self.M:
                    break

            borrow = self._multiply_and_subtract(u, v, q_hat, j, n)

            if borrow:
                q_hat -= 1
                self._add_back(u, v, j, n)

            q[j] = q_hat

        while len(q) > 1 and q[-1] == 0:
            q.pop()

        result_sign = self.sign != divisor.sign
        return LongNumber(self.M, max(self.N, divisor.N), q, result_sign)

    def _multiply_and_subtract(self, u, v, q_hat, j, n):
        carry = 0
        borrow = 0

        for i in range(n):
            product = v.__data__[i] * q_hat + carry
            carry = product // self.M
            product_digit = product % self.M

            if u.__data__[j + i] < product_digit + borrow:
                u.__data__[j + i] += self.M - product_digit - borrow
                borrow = 1
            else:
                u.__data__[j + i] -= product_digit + borrow
                borrow = 0

        if u.__data__[j + n] < carry + borrow:
            u.__data__[j + n] += self.M - carry - borrow
            return 1
        else:
            u.__data__[j + n] -= carry + borrow
            return 0

    def _add_back(self, u, v, j, n):
        carry = 0
        for i in range(n):
            sum_digit = u.__data__[j + i] + v.__data__[i] + carry
            carry = sum_digit // self.M
            u.__data__[j + i] = sum_digit % self.M
        u.__data__[j + n] += carry

    def __abs__(self):
        return LongNumber(self.M, self.N, self.__data__)

    def __lt__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            raise ValueError("M must be equal for both operands")

        if not self.sign and other.sign:
            return False
        if self.sign and not other.sign:
            return True

        return self._compare_abs(other) < 0

    def __eq__(self, other):
        if not isinstance(other, LongNumber):
            return NotImplemented
        if self.M != other.M:
            return False

        return self.sign == other.sign and self._compare_abs(other) == 0

    def _compare_abs(self, other):
        len_self = len(self.__data__)
        len_other = len(other.__data__)

        while len_self > 1 and self.__data__[len_self - 1] == 0:
            len_self -= 1
        while len_other > 1 and other.__data__[len_other - 1] == 0:
            len_other -= 1

        if len_self != len_other:
            return -1 if len_self < len_other else 1

        for i in range(len_self - 1, -1, -1):
            if self.__data__[i] != other.__data__[i]:
                return -1 if self.__data__[i] < other.__data__[i] else 1

        return 0


def main():
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
    b = LongNumber(100, 3, 9999, False)

    print(a, ' + ', b, ' = ', a + b)
    print(a, ' - ', b, ' = ', a - b)
    print(a, ' // ', b, ' = ', a // b)

    c = LongNumber(10, 3, "10")
    print(c, ' * ', c, ' = ', c * c)

    e = LongNumber(10, 3, "165")
    print(c, ' * ', c, ' = ', c * c)
    d = LongNumber(10, 6, 994989)

    print(e, ' + ', d, ' = ', e + d)
    print(e, ' - ', d, ' = ', e - d)
    print(d, ' // ', e, ' = ', d // e)
    # print(c, ' * ', d, ' = ', c * d) # OverflowError

    f = LongNumber(10, 1, 6)
    print(f, ' * ', e, ' = ', f * e)

    f = LongNumber(10, 1, 7)
    print(f, ' * ', e, ' = ', f * e) # OverflowError

if __name__ == '__main__':
    main()
