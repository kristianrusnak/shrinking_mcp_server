from node2vec import Node2Vec

from embedding.embedding.graph_builder import *


def embed_graph(G: nx.Graph, dimensions=64, walk_length=30, num_walks=100):
    """
    Generates graph embeddings using the Node2Vec algorithm.

    This function takes a graph as input and computes an embedding representation
    for its nodes. It trains a Node2Vec model given specified parameters
    and returns the averaged embedding that summarizes the graph.

    :param G: The input graph as a NetworkX graph object.
    :param dimensions: The number of dimensions for the embeddings.
    :param walk_length: The length of each random walk performed during training.
    :param num_walks: The number of random walks per node.
    :return: A numpy array representing the averaged embedding of the graph nodes.
    """
    # train node2vec
    n2v = Node2Vec(G, dimensions=dimensions,
                   walk_length=walk_length, num_walks=num_walks,
                   workers=4,
                   quiet=True)
    model = n2v.fit(window=10, min_count=1)

    # create embedding matrix
    node_list = list(G.nodes())
    emb = np.vstack([model.wv[str(n)] for n in node_list])
    return np.mean(emb, axis=0)


def embed_graph_structural(G: nx.Graph) -> np.ndarray:
    """
    Generate a structural embedding of a graph by combining various graph
    features that represent its structure. This function extracts features
    including the degree histogram, cycle-related metrics, hierarchy depth,
    strongly connected component size histogram, and centrality-based rank
    vector.

    :param G: A networkx graph instance for which the structural embedding
              is computed.
    :type G: nx.Graph
    :return: A concatenated numpy array containing the computed structural
             embeddings of the input graph by combining all extracted
             features.
    :rtype: np.ndarray
    """
    return np.concatenate([
        normalized_degree_histogram(G, bins=5),
        np.array([cycle_ratio(G)]),
        np.array([hierarchy_depth(G)]),
        scc_size_histogram(G, bins=5),
        centrality_rank_vector(G, k=5)
    ])
