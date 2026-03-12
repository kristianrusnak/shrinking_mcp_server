import networkx as nx
import numpy as np


def uml_dict_to_graph(uml: dict) -> nx.DiGraph:
    """
    Converts a UML representation provided as a dictionary into a directed graph
    using `networkx.DiGraph`. The graph captures the relationships, attributes,
    and structure defined within the UML dictionary.

    :param uml: Dictionary representing the UML structure. It should contain
        the following keys:
        - "classes": A dictionary where keys are class names and values contain
          attributes for each class (e.g., "attributes", "methods").
        - "edges": A list of dictionaries, each representing a relationship
          between classes (e.g., "source", "target", "relation").
    :type uml: dict
    :return: A directed graph where nodes represent classes with associated
        metadata attributes and edges represent class relationships based on
        the provided UML.
    :rtype: nx.DiGraph
    """
    G = nx.DiGraph()
    classes = list(uml.get("classes", {}).keys())

    name_to_id = {name: i for i, name in enumerate(classes)}

    # Add nodes with attributes
    for i, cls_name in enumerate(classes):
        cls_data = uml["classes"][cls_name]
        num_attrs = len(cls_data.get("attributes", []))
        num_methods = len(cls_data.get("methods", []))
        attr_types = [attr["datatype"] for attr in cls_data.get("attributes", [])]
        G.add_node(i,
                   label="Class",
                   name=cls_name,
                   num_attributes=num_attrs,
                   num_methods=num_methods,
                   attr_types=attr_types)

    # Add edges with relation types
    for edge in uml.get("edges", []):
        src = name_to_id.get(edge["source"])
        tgt = name_to_id.get(edge["target"])
        if src is not None and tgt is not None:
            G.add_edge(src, tgt, relation=edge.get("relation", "unknown"))

    return G


def normalized_degree_histogram(G, bins=5):
    degrees = [d for _, d in G.degree()]
    if not degrees:
        return np.zeros(bins)

    hist, _ = np.histogram(degrees, bins=bins, range=(0, max(degrees)))
    hist = hist.astype(float)
    return hist / hist.sum()

def cycle_ratio(G):
    if G.number_of_edges() == 0:
        return 0.0

    try:
        cycles = nx.simple_cycles(G) if G.is_directed() else nx.cycle_basis(G)
        num_cycles = len(list(cycles))
    except Exception:
        num_cycles = 0

    return min(1.0, num_cycles / G.number_of_edges())

def hierarchy_depth(G):
    if G.number_of_nodes() == 0:
        return 0.0

    if not G.is_directed():
        return 0.0

    scc_graph = nx.condensation(G)

    if not nx.is_directed_acyclic_graph(scc_graph):
        return 0.0

    depth = nx.dag_longest_path_length(scc_graph)
    return depth / max(1, G.number_of_nodes())

def scc_size_histogram(G, bins=5):
    if not G.is_directed():
        return np.zeros(bins)

    sccs = list(nx.strongly_connected_components(G))
    sizes = [len(scc) for scc in sccs]

    if not sizes:
        return np.zeros(bins)

    hist, _ = np.histogram(sizes, bins=bins, range=(1, max(sizes)))
    hist = hist.astype(float)
    return hist / hist.sum()

def centrality_rank_vector(G, k=5):
    if G.number_of_nodes() == 0:
        return np.zeros(k)

    centrality = nx.betweenness_centrality(G, normalized=True)
    ranked = sorted(centrality.values(), reverse=True)

    ranked = ranked[:k]
    if len(ranked) < k:
        ranked += [0.0] * (k - len(ranked))

    ranked = np.array(ranked)
    if ranked.sum() == 0:
        return ranked

    return ranked / ranked.sum()
