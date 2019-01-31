from simple_models.bridge_model import BridgeModel

bridge_model = BridgeModel(1, 1, {'board': [-1, -1, -1, -1], 'lefts': [0, 0],
                                  'hands': BridgeModel.generate_random_hands(1, 1), 'next': 0, 'history': [],
                                  'beginning': 0, 'clock': 0, 'suit': -1})
