class DisjointSet:
    subsets = []

    def __init__(self, number_of_nodes):
        for i in range(0, number_of_nodes):
            self.subsets.append({'parent': i, 'rank': 0})

    def find(self, node_number):
        if self.subsets[node_number].parent != node_number:
            self.subsets[node_number] = self.find(self.subsets[node_number].parent)

        return self.subsets[node_number].parent

    def union(self, x, y):
        xRoot = self.find(x)
        yRoot = self.find(y)

        if self.subsets[xRoot].rank < self.subsets[yRoot].rank:
            self.subsets[xRoot].parent = yRoot
        elif self.subsets[xRoot].rank > self.subsets[yRoot].rank:
            self.subsets[yRoot].parent = xRoot
        else:
            self.subsets[yRoot].parent = xRoot
            self.subsets[xRoot].rank += 1
