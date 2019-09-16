class NumberTools:
    @staticmethod
    def max(a: int, b: int) -> int:
        """
        Returns larger of the two numbers
        :param a: first number
        :param b: second number
        :return: larger of the two numbers
        """
        return a if a > b else b

    @staticmethod
    def min(a: int, b: int) -> int:
        """
        Returns smaller of the two numbers
        :param a: first number
        :param b: second number
        :return: smaller of the two numbers
        """
        return a if a < b else b