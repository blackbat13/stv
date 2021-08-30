from typing import Dict

class TestResult:
    tGenAverage: float
    tVerifLowerOrig: float
    tVerifUpperOrig: float
    resultLowerOrig: bool
    resultUpperOrig: bool
    tVerifLowerOpt: float
    tVerifUpperOpt: float
    resultLowerOpt: bool
    resultUpperOpt: bool
    params: Dict[str, int]
    
    def __init__(self):
        self.tGenAverage = 0
        self.tVerifLowerOrig = 0
        self.tVerifUpperOrig = 0
        self.resultLowerOrig = None
        self.resultUpperOrig = None
        self.tVerifLowerOpt = 0
        self.tVerifUpperOpt = 0
        self.resultLowerOpt = None
        self.resultUpperOpt = None
        self.params = {}
