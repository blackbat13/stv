"""Module for the disjoint-set-union structure."""


class DisjointSet:
    """
    Class representing Disjoint-Set-Union structure.
    :param number_of_nodes: how many elements should be store in the structure.
    :ivar _subsets: information about subsets
    """

    def __init__(self, number_of_nodes: int):
        self._subsets = []
        for i in range(0, number_of_nodes):
            self._subsets.append({'parent': i, 'rank': 0})

    def union(self, el1: int, el2: int) -> None:
        """
        Union two elements.
        :param el1: First element.
        :param el2: Second element.
        :return: None
        """
        x_root = self.find(el1)
        y_root = self.find(el2)

        if self._subsets[x_root]['rank'] < self._subsets[y_root]['rank']:
            self._subsets[x_root]['parent'] = y_root
        elif self._subsets[x_root]['rank'] > self._subsets[y_root]['rank']:
            self._subsets[y_root]['parent'] = x_root
        else:
            self._subsets[y_root]['parent'] = x_root
            self._subsets[x_root]['rank'] += 1

    def is_in_union(self, el1: int, el2: int) -> bool:
        """
        Checks if two elements are in union i.e. have the same representative.
        :param el1: First element.
        :param el2: Second element.
        :return: True if x and y are in union, False otherwise.
        """
        return self.find(el1) == self.find(el2)

    def find(self, node_number: int):
        """
        Find the representative of a given element.
        :param node_number: element to check
        :return: Representative of the node_number element in the structure.
        """
        if self._subsets[node_number]['parent'] != node_number:
            self._subsets[node_number]['parent'] = self.find(self._subsets[node_number]['parent'])

        return self._subsets[node_number]['parent']
