import json
import os
import random
from typing import Any, Dict

import numpy as np

from .base import ShrinkingAlgorithm
from embedding.embedding import uml_dict_to_graph, embed_graph


class GeneticAlgorithm(ShrinkingAlgorithm):
    """
    Genetic Algorithm for diagram shrinking.
    Implements ShrinkingAlgorithm interface.

    Each individual is a vector where each position represents a diagram element.
    Values 0-0.5: element excluded
    Values 0.6-1: element included
    """

    def initialize(self, **params: Any) -> None:
        """
        Initialize the algorithm with parameters.

        Supported parameters:
        - config_path: path to JSON config file
        - population_size: size of GA population
        - generations: number of generations to run
        - mutation_rate: probability of mutation
        - crossover_rate: probability of crossover
        - exclusion_threshold: threshold below which elements are excluded
        - inclusion_threshold: threshold above which elements are included
        """
        config_path = params.get("config_path", "ga_config.json")
        self.config = self.load_config(config_path)

        self.population_size = params.get("population_size", self.config.get("population_size", 50))
        self.generations = params.get("generations", self.config.get("generations", 100))
        self.mutation_rate = params.get("mutation_rate", self.config.get("mutation_rate", 0.1))
        self.crossover_rate = params.get("crossover_rate", self.config.get("crossover_rate", 0.7))
        self.exclusion_threshold = params.get("exclusion_threshold", self.config.get("exclusion_threshold", 0.5))
        self.inclusion_threshold = params.get("inclusion_threshold", self.config.get("inclusion_threshold", 0.6))

        upper_limit = params.get("upper_limit", self.config.get("upper_limit", 100))
        lower_limit = params.get("lower_limit", self.config.get("lower_limit", 1))

        self.population_size = max(lower_limit, min(upper_limit, self.population_size))
        self.generations = max(lower_limit, min(upper_limit, self.generations))

        self.elements = []
        self.element_types = []
        self.population = []
        self.best_individual = None
        self.best_fitness = -float('inf')
        self.original_embedding = None
        self.G_full = None

    def load_config(self, config_path):
        """Load docker configuration from JSON file."""

        base_path = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_path, config_path)

        try:
            with open(full_path, "r") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}

    def compute(self, parsed_puml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the genetic algorithm on parsed PUML data and return the reduced PUML data.

        Args:
            parsed_puml: Dictionary with 'classes' and 'edges' keys

        Returns:
            Reduced PUML dictionary with same structure
        """
        self.PUML = parsed_puml
        self._extract_elements()
        self.G_full = uml_dict_to_graph(self.PUML)
        self.original_embedding = embed_graph(self.G_full)

        best_individual = self.solve()
        reduced_diagram = self.extract_solution(best_individual)

        return reduced_diagram

    def _extract_elements(self):
        """
        Extract all diagram elements (classes, edges, attributes, methods).
        Each element gets an index in the individual vector.
        """
        self.elements = []
        self.element_types = []

        for class_name in self.PUML["classes"].keys():
            self.elements.append(("class", class_name, None))
            self.element_types.append("class")

            for attr in self.PUML["classes"][class_name].get("attributes", []):
                self.elements.append(("attribute", class_name, attr))
                self.element_types.append("attribute")

            for method in self.PUML["classes"][class_name].get("methods", []):
                self.elements.append(("method", class_name, method))
                self.element_types.append("method")

        for edge in self.PUML["edges"]:
            self.elements.append(("edge", edge, None))
            self.element_types.append("edge")

    def initialize_population(self):
        """Generate initial random population."""
        self.population = []
        for _ in range(self.population_size):
            individual = [random.random() for _ in range(len(self.elements))]
            self.population.append(individual)

    def fitness_function(self, individual):
        """
        Evaluate fitness of an individual.
        """

        G_shrunk = uml_dict_to_graph(self.decode_individual(individual))

        emb_orig = self.original_embedding
        emb_shrunk = embed_graph(G_shrunk)

        similarity = self._cosine_sim(emb_orig, emb_shrunk)

        compression_ratio = (
            (len(self.G_full) - len(G_shrunk)) / len(self.G_full)
        )
        compression_ratio = max(compression_ratio, 1e-8)

        return similarity / compression_ratio


    def selection(self):
        """
        Tournament selection: pick random individuals and select the best.
        Returns selected parents for reproduction.
        """
        tournament_size = 3
        selected = []

        for _ in range(self.population_size):
            tournament = random.sample(self.population, tournament_size)
            tournament_fitness = [(ind, self.fitness_function(ind)) for ind in tournament]
            winner = max(tournament_fitness, key=lambda x: x[1])
            selected.append(winner[0])

        return selected

    def crossover(self, parent1, parent2):
        """
        Single-point crossover: create two offspring from two parents.
        """
        if random.random() > self.crossover_rate:
            return parent1[:], parent2[:]

        crossover_point = random.randint(1, len(parent1) - 1)

        offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
        offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

        return offspring1, offspring2

    def mutate(self, individual):
        """
        Mutation: randomly change some genes (float values in [0,1]).
        """
        mutated = individual[:]

        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutated[i] = random.random()


        return mutated

    def solve(self):
        """
        Run the genetic algorithm for specified number of generations.
        Returns the best individual found.
        """
        self.initialize_population()

        for generation in range(self.generations):
            print(f"Generation {generation + 1}")
            fitness_values = [(ind, self.fitness_function(ind)) for ind in self.population]

            current_best = max(fitness_values, key=lambda x: x[1])
            if current_best[1] > self.best_fitness:
                self.best_fitness = current_best[1]
                self.best_individual = current_best[0][:]

            selected = self.selection()
            new_population = []

            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i + 1] if i + 1 < len(selected) else selected[0]

                offspring1, offspring2 = self.crossover(parent1, parent2)

                offspring1 = self.mutate(offspring1)
                offspring2 = self.mutate(offspring2)

                new_population.extend([offspring1, offspring2])

            self.population = new_population[:self.population_size]

        return self.best_individual

    def decode_individual(self, individual):
        """
        Convert individual vector to diagram structure.
        Elements with value > inclusion_threshold are included.
        """
        included_classes = {}
        included_edges = []

        for i, value in enumerate(individual):
            if value >= self.inclusion_threshold:
                element_type, key, data = self.elements[i]

                if element_type == "class":
                    if key not in included_classes:
                        included_classes[key] = {
                            "id": self.PUML["classes"][key]["id"],
                            "attributes": [],
                            "methods": []
                        }

                elif element_type == "attribute":
                    class_name = key
                    if class_name not in included_classes:
                        included_classes[class_name] = {
                            "id": self.PUML["classes"][class_name]["id"],
                            "attributes": [],
                            "methods": []
                        }
                    included_classes[class_name]["attributes"].append(data)

                elif element_type == "method":
                    class_name = key
                    if class_name not in included_classes:
                        included_classes[class_name] = {
                            "id": self.PUML["classes"][class_name]["id"],
                            "attributes": [],
                            "methods": []
                        }
                    included_classes[class_name]["methods"].append(data)

                elif element_type == "edge":
                    edge = key
                    source = edge["source"]
                    target = edge["target"]

                    if source in self.PUML["classes"] and target in self.PUML["classes"]:
                        if source not in included_classes:
                            included_classes[source] = {
                                "id": self.PUML["classes"][source]["id"],
                                "attributes": [],
                                "methods": []
                            }
                        if target not in included_classes:
                            included_classes[target] = {
                                "id": self.PUML["classes"][target]["id"],
                                "attributes": [],
                                "methods": []
                            }
                        included_edges.append(edge)

        return {"classes": included_classes, "edges": included_edges}

    def extract_solution(self, individual):
        """
        Convert the best individual to a reduced PUML diagram structure.
        Compatible with PUMLParser.reparse_file() method.
        """
        return self.decode_individual(individual)

    def _cosine_sim(self, a, b):
        a = a.ravel()
        b = b.ravel()
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
