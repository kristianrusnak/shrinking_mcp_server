from abc import ABC, abstractmethod
from typing import Any, Dict

class ShrinkingAlgorithm(ABC):
    """
    Interface for all diagram-shrinking algorithms.
    """

    def __init__(self, **params: Any) -> None:
        """
        Optional shared init – you can store hyperparameters here.
        """
        self.initialize(**params)

    @abstractmethod
    def initialize(self, **params: Any) -> None:
        """
        Initialize the algorithm with parameters (weights, thresholds, etc.).
        """
        pass

    @abstractmethod
    def compute(self, parsed_puml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the algorithm on parsed PUML data and return the reduced PUML data.
        """
        pass
