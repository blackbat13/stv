from simple_models.dining_cryptographers import DiningCryptographers
from comparing_strats.graph_drawing import GraphDrawing

diningCryptographers = DiningCryptographers(3)
diningCryptographers.generate()
model = diningCryptographers.model
strategy = []

for i in range(0, len(model.states)):
    strategy.append(None)


graphDrawing = GraphDrawing(model, strategy)
graphDrawing.draw()
