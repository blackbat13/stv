no_states = 4
no_agents = 2

graph = []

for i in range(0, no_states):
    graph.append([])


# For each state add transitions coming from that state
graph[0].append({"nextState": 1, "actions": ["Push", "Wait"]})
graph[0].append({"nextState": 0, "actions": ["Wait", "Wait"]})
graph[0].append({"nextState": 0, "actions": ["Push", "Push"]})
graph[0].append({"nextState": 3, "actions": ["Wait", "Push"]})

graph[1].append({"nextState": 2, "actions": ["Push", "Wait"]})
graph[1].append({"nextState": 1, "actions": ["Wait", "Wait"]})
graph[1].append({"nextState": 1, "actions": ["Push", "Push"]})
graph[1].append({"nextState": 0, "actions": ["Wait", "Push"]})

graph[2].append({"nextState": 3, "actions": ["Push", "Wait"]})
graph[2].append({"nextState": 2, "actions": ["Wait", "Wait"]})
graph[2].append({"nextState": 2, "actions": ["Push", "Push"]})
graph[2].append({"nextState": 1, "actions": ["Wait", "Push"]})

graph[3].append({"nextState": 0, "actions": ["Push", "Wait"]})
graph[3].append({"nextState": 3, "actions": ["Wait", "Wait"]})
graph[3].append({"nextState": 3, "actions": ["Push", "Push"]})
graph[3].append({"nextState": 2, "actions": ["Wait", "Push"]})

epistemic_classes = []

for i in range(0, no_agents):
    epistemic_classes.append([])

# For each agent epistemic_classes holds sets of states belonging to one epistemic class
epistemic_classes[0].append({0, 1, 2})
epistemic_classes[1].append({0, 2, 3})

print(graph)
print(epistemic_classes)