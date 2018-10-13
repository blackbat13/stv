class ArrayTools:
    @staticmethod
    def create_array_of_size(size: int, basic_item) -> list:
        """Creates array of given size containing copies of given items"""
        array = []
        for i in range(0, size):
            array.append(basic_item.copy())
        return array[:]

    @staticmethod
    def create_value_array_of_size(size: int, basic_value):
        """Creates array of given size containing given value"""
        array = []
        for i in range(0, size):
            array.append(basic_value)
        return array[:]

    @staticmethod
    def unique(l: list):
        """Removes all duplicates from list"""
        s = set()
        n = 0
        for x in l:
            if x not in s:
                s.add(x)
                l[n] = x
                n += 1
        del l[n:]