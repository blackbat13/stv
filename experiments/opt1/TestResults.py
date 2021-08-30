from typing import List
from TestResult import TestResult

class TestResults:
    _results: List[TestResult] = []
    
    def add(self, testResult):
        self._results.append(testResult)
    
    def __repr__(self) -> str:
        s = ""
        if len(self._results) == 0:
            return "(no results)"
        paramNames = self._results[0].params.keys()
        for p in paramNames:
            s += p + "    "
        s += "       tGen         tVerifLower         tVerifUpper    resLower    resUpper         tVerifLower         tVerifUpper    resLower    resUpper\n"
        for r in self._results:
            for p in paramNames:
                f = "{:" + str(len(p)) + "d}"
                s += f.format(r.params[p]) + "    "
            s += " {:10.3f}".format(r.tGenAverage) + "    "
            s += "      {:10.3f}".format(r.tVerifLowerOrig) + "    "
            s += "      {:10.3f}".format(r.tVerifUpperOrig) + "    "
            s += "   " + str(r.resultLowerOrig) + "    "
            s += "   " + str(r.resultUpperOrig) + "    "
            s += "      {:10.3f}".format(r.tVerifLowerOpt) + "    "
            s += "      {:10.3f}".format(r.tVerifUpperOpt) + "    "
            s += "   " + str(r.resultLowerOpt) + "    "
            s += "   " + str(r.resultUpperOpt) + "\n"
        return s
