from comparing_strats.simple_model import SimpleModel
import networkx
import matplotlib.pyplot as plt


class GraphDrawing:
    model = None

    def __init__(self, model: SimpleModel):
        self.model = model

    def draw(self):
        graph = networkx.Graph()
        no_states = len(self.model.states)
        for i in range(0, no_states):
            graph.add_node(i)

        for state in range(0, no_states):
            for transition in self.model.graph[state]:
                next_state = transition['next_state']
                graph.add_edges_from([(state, next_state)],
                                     label=transition['actions'])  # {'actions': transition['actions']}

        plt.subplot(121)
        # pos = networkx.graphviz_layout(graph, scale=10)
        # networkx.draw_kamada_kawai(graph)
        # pos = networkx.spring_layout(graph, k=1, iterations=20)
        pos = networkx.drawing.nx_agraph.graphviz_layout(graph, prog='dot', root=0)

        networkx.draw(graph, pos=pos, with_labels=True, font_weight='bold')
        networkx.draw_networkx_edge_labels(graph, pos=pos)
        plt.show()
