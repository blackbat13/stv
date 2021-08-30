import json
import sys
import time
from typing import List
from TestResult import TestResult
from TestResults import TestResults
sys.path.append("../..")
from stv.models import BridgeModel

class BridgeEndplayTest:
    
    _agentId = 0
    
    def run(self):
        testResults = TestResults()
        for p in range(1, 3):
        # for p in range(1, 5):
            testResult = self._runSingle(p, p)
            testResults.add(testResult)
        print(testResults)
    
    def _runSingle(self, deckSize: int, cardsInHand: int):
        hands = BridgeModel.generate_random_hands(deckSize, cardsInHand)
        
        tGen0_orig = time.time()
        modelU_orig = self._generateModel(deckSize, cardsInHand, hands)
        modelL_orig = self._generateModel(deckSize, cardsInHand, hands)
        tGen1_orig = time.time()
        
        tVerifU0_orig = time.time()
        atlModelU_orig = modelU_orig.model.to_atl_perfect(modelU_orig.get_actions())
        resultU_orig = self._getResult(modelU_orig, atlModelU_orig, cardsInHand)
        tVerifU1_orig = time.time()
        
        tVerifL0_orig = time.time()
        atlModelL_orig = modelL_orig.model.to_atl_imperfect(modelL_orig.get_actions())
        resultL_orig = self._getResult(modelL_orig, atlModelL_orig, cardsInHand)
        tVerifL1_orig = time.time()
        
        tGen0_opt = time.time()
        modelU_opt = self._generateModel(deckSize, cardsInHand, hands)
        modelL_opt = self._generateModel(deckSize, cardsInHand, hands)
        tGen1_opt = time.time()
        
        tVerifU0_opt = time.time()
        atlModelU_opt = modelU_opt.model.to_atl_perfect(modelU_opt.get_actions(), True)
        resultU_opt = self._getResult(modelU_opt, atlModelU_opt, cardsInHand)
        tVerifU1_opt = time.time()
        
        tVerifL0_opt = time.time()
        modelL_opt.model.dropNotVisitedStates(atlModelU_opt.visitedStates)
        atlModelL_opt = modelL_opt.model.to_atl_imperfect(modelL_opt.get_actions())
        resultL_opt = self._getResult(modelL_opt, atlModelL_opt, cardsInHand)
        tVerifL1_opt = time.time()
        
        testResult = TestResult()
        testResult.params["deckSize"] = deckSize
        testResult.params["cardsInHand"] = cardsInHand
        testResult.tGenAverage = ((tGen1_orig - tGen0_orig) + (tGen1_opt - tGen0_opt)) / 4
        testResult.tVerifUpperOrig = tVerifU1_orig - tVerifU0_orig
        testResult.tVerifLowerOrig = tVerifL1_orig - tVerifL0_orig
        testResult.resultUpperOrig = 0 in resultU_orig
        testResult.resultLowerOrig = 0 in resultL_orig
        testResult.tVerifUpperOpt = tVerifU1_opt - tVerifU0_opt
        testResult.tVerifLowerOpt = tVerifL1_opt - tVerifL0_opt
        testResult.resultUpperOpt = 0 in resultU_opt
        testResult.resultLowerOpt = 0 in resultL_opt
        return testResult
    
    def _generateModel(self, deckSize, cardsInHand, hands):
        model = BridgeModel(
            deckSize,
            cardsInHand,
            {
                "board": [-1, -1, -1, -1],
                "lefts": [0, 0],
                "hands": hands,
                "next": 0,
                "history": [],
                "beginning": 0,
                "clock": 0,
                "suit": -1,
            },
        )
        model.generate()
        model.transitions_to_readable()
        return model
    
    def _getResult(self, model, atlModel, cardsInHand):
        winning = self._getWinningStates(model.states, cardsInHand)
        result = atlModel.minimum_formula_many_agents([self._agentId], winning)
        return result
    
    def _getWinningStates(self, states: List[hash], cardsInHand: int):
        winning = set()
        stateId = -1
        for state in states:
            stateId += 1
            if state["lefts"][0] > state["lefts"][1] and state["lefts"][0] + state["lefts"][1] == cardsInHand:
                winning.add(stateId)
        return winning

if __name__ == "__main__":
    test = BridgeEndplayTest()
    test.run()
