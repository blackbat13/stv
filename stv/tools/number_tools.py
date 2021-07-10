"""Module for number tools."""


class NumberTools:
    """
    Collection of methods to simplify working with numbers.
    """

    @staticmethod
    def max(num1: int, num2: int) -> int:
        """
        Returns larger of the two numbers
        :param num1: first number
        :param num2: second number
        :return: larger of the two numbers

        Example:
        >>> NumberTools.max(2, 5)
        5
        """
        return num1 if num1 > num2 else num2

    @staticmethod
    def min(num1: int, num2: int) -> int:
        """
        Returns smaller of the two numbers
        :param num1: first number
        :param num2: second number
        :return: smaller of the two numbers

        Example:
        >>> NumberTools.min(2, 5)
        2
        """
        return num1 if num1 < num2 else num2
