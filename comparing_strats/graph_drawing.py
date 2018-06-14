from comparing_strats.simple_model import SimpleModel
import networkx
import matplotlib.pyplot as plt


class GraphDrawing:
    model = None

    def __init__(self, model: SimpleModel):
        self.model = model

    def draw(self):
        graph = networkx.DiGraph()
        no_states = len(self.model.states)
        for i, state in enumerate(self.model.states):
            label = ''
            for key in state:
                label += f'{key}:{state[key]}\n'
            graph.add_node(i, label=label)

        for state in range(0, no_states):
            for transition in self.model.graph[state]:
                next_state = transition['next_state']
                graph.add_edges_from([(state, next_state)],
                                     label=transition['actions'])

        plt.figure(1, figsize=(50, 10))
        plt.subplot(111)
        pos = networkx.drawing.nx_agraph.graphviz_layout(graph, prog='dot', root=0)

        labels = networkx.get_edge_attributes(graph, 'label')
        networkx.draw(graph, pos=pos, with_labels=False, font_weight='bold')
        networkx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=labels)
        networkx.draw_networkx_labels(graph, pos=pos, labels=networkx.get_node_attributes(graph, 'label'))
        plt.autoscale()
        plt.show()
