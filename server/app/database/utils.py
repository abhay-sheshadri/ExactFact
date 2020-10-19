from app.database.database import *
import os
from app import config
from annoy import AnnoyIndex

trees = None

def load_structures():
    """
    Loads the database and the binary trees
    """
    # Open database and/or load dict
    open_database()
    # Load trees
    if os.path.isfile(os.path.join("app", "database", "trees.ann")):
        load_trees_from_file()
    else:
        construct_trees_from_database()


def construct_trees_from_database():
    global trees
    # Creates a new index
    trees = AnnoyIndex(config["vector_dim"], "euclidean")
    for key, vector in get_all_keys_and_vectors():
        trees.add_item(key, vector)
    trees.build(config["n_trees"])
    trees.save( os.path.join("app", "database", "trees.ann") )


def load_trees_from_file():
    # loads trees from file
    global trees
    trees = AnnoyIndex(config["vector_dim"], "euclidean")
    trees.load( os.path.join("app", "database", "trees.ann") )


def get_similar_misinformation(sentence):
    # Wraps the method below so that it runs for multiple vectors within a sentence
    most_similar = set()
    for vector in sentence.embeddings:
        for key in get_most_similar(vector):
            most_similar.add(key)
    # Return the keys and their associated data
    return [{
        "error": p[0],
        "source": p[1],
        "correct": p[2]
    } for p in get_return_from_keys(most_similar)]


def get_most_similar(vector):
    # Search the loaded trees
    global trees
    # Search
    keys, distances = trees.get_nns_by_vector(vector, config["max_results_per_query"], search_k=config["search_k"], include_distances=True)
    # return the keys that are over the distance
    return [keys[i] for i in range(len(keys)) if distances[i] <= config["max_dist"]]
