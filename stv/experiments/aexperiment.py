from abc import ABC, abstractmethod


class AExperiment(ABC):
    """Abstract class for the experiments"""

    def __init__(self, DEBUG: bool = False):
        self._DEBUG = DEBUG
        self._results_file = None
        self._file_name = "results_file.txt"
        self._model = None

    def run_experiments(self):
        self._open_results_file()
        self._write_file_header()
        self._generate_model()
        self._run_mc()
        self._write_result()
        self._close_results_file()

    def _open_results_file(self):
        self._results_file = open(self._file_name, "a")

    @abstractmethod
    def _write_file_header(self):
        pass

    @abstractmethod
    def _generate_model(self):
        pass

    @abstractmethod
    def _run_mc(self):
        pass

    @abstractmethod
    def _write_result(self):
        pass

    def _close_results_file(self):
        self._results_file.close()
