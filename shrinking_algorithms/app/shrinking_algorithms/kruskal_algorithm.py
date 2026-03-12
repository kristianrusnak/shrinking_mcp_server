import os
import json
from typing import Any, Dict
from .base import ShrinkingAlgorithm

class KruskalsAlgorithm(ShrinkingAlgorithm):
    """
    Kruskal's MST algorithm for diagram shrinking.
    Implements ShrinkingAlgorithm interface.
    """

    def initialize(self, **params: Any) -> None:
        """
        Initialize the algorithm with parameters.

        Supported parameters:
        - config_path: path to JSON config file with weights mapping
        """
        config_path = params.get("config_path", "kruskals_config.json")
        self.weights_map = self.load_weights(config_path)

        self.PUML = None
        self.size = 0
        self.edges = []
        self.vertex_data = []

    def load_weights(self, config_path):
        """Load weights mapping from JSON config file."""
        # in docker container paths are different
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, config_path)

        try:
            with open(full_path, "r") as file:
                config = json.load(file)
                return config.get("weights", {})
        except Exception as e:
            print(f"Error loading config file: {e}")
            return {}

    def get_weight(self, association_type):
        """Get weight for given association type from config."""
        if association_type in self.weights_map:
            return self.weights_map[association_type]

        association_lower = association_type.lower().strip()
        for key, value in self.weights_map.items():
            if key.lower().strip() == association_lower:
                return value

        return 1

    def compute(self, parsed_puml: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Kruskal's algorithm on parsed PUML data and return the MST.

        Args:
            parsed_puml: Dictionary with 'classes' and 'edges' keys

        Returns:
            Reduced PUML dictionary with MST edges
        """
        self.PUML = parsed_puml
        self.size = len(parsed_puml["classes"])
        self.edges = []
        self.vertex_data = [''] * self.size

        self.extract_puml_data(parsed_puml)
        return self.solve()

    def extract_puml_data(self, PUML):
        for class_name, class_info in PUML["classes"].items():
            index = class_info["id"]
            self.add_vertex_data(index, class_name)

        for edge in PUML["edges"]:
            source = edge["source"]
            target = edge["target"]

            association_type = edge.get("type", "association")
            weight = self.get_weight(association_type)

            if source in PUML["classes"] and target in PUML["classes"]:
                u = PUML["classes"][source]["id"]
                v = PUML["classes"][target]["id"]
                self.add_edge(u, v, weight)

    def add_edge(self, u, v, weight):
        if 0 <= u < self.size and 0 <= v < self.size:
            self.edges.append((u, v, weight))  # Add edge with weight

    def add_vertex_data(self, vertex, data):
        if 0 <= vertex < self.size:
            self.vertex_data[vertex] = data

    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)
        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        else:
            parent[yroot] = xroot
            rank[xroot] += 1

    def solve(self):
        result = []  # MST
        i = 0  # edge counter

        self.edges = sorted(self.edges, key=lambda item: item[2])

        parent, rank = [], []

        for node in range(self.size):
            parent.append(node)
            rank.append(0)

        while i < len(self.edges):
            u, v, weight = self.edges[i]
            i += 1
            x = self.find(parent, u)
            y = self.find(parent, v)
            if x != y:
                result.append((u, v, weight))
                self.union(parent, rank, x, y)

        return self.extract_solution(result)

    def extract_solution(self, sol):
        edges = []

        edge_lookup = {}
        for edge in self.PUML["edges"]:
            source = edge["source"]
            target = edge["target"]
            u = self.PUML["classes"][source]["id"]
            v = self.PUML["classes"][target]["id"]
            edge_lookup[(u, v)] = edge
            edge_lookup[(v, u)] = edge

        edge_lookup = {}
        for edge in self.PUML["edges"]:
            source = edge["source"]
            target = edge["target"]
            u = self.PUML["classes"][source]["id"]
            v = self.PUML["classes"][target]["id"]
            edge_lookup[(u, v)] = edge
            edge_lookup[(v, u)] = edge

        for u, v, weight in sol:
            original_edge = edge_lookup.get((u, v), edge_lookup.get((v, u)))

            if original_edge:
                edges.append(original_edge)

        return {"classes": self.PUML["classes"], "edges": edges}
