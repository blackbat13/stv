"""Module for list tools."""


class ListTools:
    """
    Collection of methods to simplify working with lists.
    """

    @staticmethod
    def create_list_of_size(size: int, basic_item) -> list:
        """
        Creates array of given size containing copies of given items
        :param size:
        :param basic_item:
        :return:
        """
        array = []
        for _ in range(0, size):
            array.append(basic_item.copy())
        return array[:]

    @staticmethod
    def create_value_list_of_size(size: int, basic_value) -> list:
        """
        Creates array of given size containing given value
        :param size:
        :param basic_value:
        :return:
        """
        array = []
        for _ in range(0, size):
            array.append(basic_value)
        return array[:]

    @staticmethod
    def unique(l: list) -> None:
        """
        Removes all duplicates from list
        :param l:
        :return:
        """
        s = set()
        n = 0
        for x in l:
            if x not in s:
                s.add(x)
                l[n] = x
                n += 1
        del l[n:]

    @staticmethod
    def count_not_none(l: list) -> int:
        """
        Counts elements with value != None
        :param l:
        :return:
        """
        count = 0
        for item in l:
            if item is not None:
                count += 1

        return count
