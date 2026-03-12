import os
from .base import ShrinkingAlgorithm
from .kruskal_algorithm import KruskalsAlgorithm
from .genetic_algorithm import GeneticAlgorithm

DEFAULT_ALGO = "kruskal"
ENV_VAR_NAME = "SHRINKING_ALGORITHM"


def get_algorithm(algorithm: str | None = None) -> ShrinkingAlgorithm:
    """
    Factory that reads env var and returns the right algorithm instance.
    """
    if not algorithm:
        name = os.getenv(ENV_VAR_NAME, DEFAULT_ALGO).lower()
    else:
        name = algorithm

    if name == "kruskal":
        return KruskalsAlgorithm()
    if name == "genetic":
        return GeneticAlgorithm()

    # later: add more algorithms here
    raise ValueError(f"Unknown algorithm: {name!r}")
