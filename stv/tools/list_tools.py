"""Module for list tools."""


class ListTools:
    """
    Collection of methods to simplify working with lists.
    """

    @staticmethod
    def unique(l: list) -> None:
        """
        Removes all duplicates from the list.
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
        Counts elements with value != None.
        :param l:
        :return:
        """
        count = 0
        for item in l:
            if item is not None:
                count += 1

        return count
