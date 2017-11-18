class DisjointSet:
    subsets = []

    def __init__(self, number_of_nodes):
        self.subsets = []
        for i in range(0, number_of_nodes):
            self.subsets.append({'parent': i, 'rank': 0})

    def find(self, node_number):
        # print(node_number)
        if self.subsets[node_number]['parent'] != node_number:
            self.subsets[node_number]['parent'] = self.find(self.subsets[node_number]['parent'])

        return self.subsets[node_number]['parent']

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)

        if self.subsets[x_root]['rank'] < self.subsets[y_root]['rank']:
            self.subsets[x_root]['parent'] = y_root
        elif self.subsets[x_root]['rank'] > self.subsets[y_root]['rank']:
            self.subsets[y_root]['parent'] = x_root
        else:
            self.subsets[y_root]['parent'] = x_root
            self.subsets[x_root]['rank'] += 1

    def is_same(self, x, y):
        return self.find(x) == self.find(y)