"""
Author: Vered Shwartz

    Receives two annotated graphs and computes the agreement on the entity coreference.
    This script returns the following scores:

    1) MUC (Vilain et al., 1995) - a link-based metric.
    2) B-CUBED (Bagga and Baldwin, 1998) - a mention-based metric.
    3) CEAF (Constrained Entity Aligned F-measure) metric (Luo, 2005) - an entity-based metric.
    4) CoNLL F1/ MELA (Denis and Baldridge, 2009) - an average of these three measures.
"""

import numpy as np

from munkres import *


def compute_node_coref_agreement(graph1, graph2):
    """
    Receives two annotated graphs and computes the agreement on the entity coreference:
    1) MUC (Vilain et al., 1995) 2) B-CUBED (Bagga and Baldwin, 1998)
    2) B-CUBED (Bagga and Baldwin, 1998) - a mention-based metric.
    3) CEAF (Luo, 2005) 4) MELA (Denis and Baldridge, 2009)
    :param graph1: the first annotator's graph
    :param graph2: the second annotator's graph
    :return: MUC, B-CUBED, CEAF and MELA scores. Each score is computed twice, each time
    a different annotator is considered as the gold, and the averaged score is returned.
    """

    # Get node mentions
    graph1_ent_mentions = [set(map(str, node.mentions.values())) for node in graph1.nodes.values()]
    graph2_ent_mentions = [set(map(str, node.mentions.values())) for node in graph2.nodes.values()]

    # Compute twice, each time considering a different annotator as the gold, and return the average among
    # each measure
    muc1, bcubed1, ceaf1 = muc(graph1_ent_mentions, graph2_ent_mentions), \
                           bcubed(graph1_ent_mentions, graph2_ent_mentions), \
                           ceaf(graph1_ent_mentions, graph2_ent_mentions)
    mela1 = np.mean([muc1, bcubed1, ceaf1])

    muc2, bcubed2, ceaf2 = muc(graph2_ent_mentions, graph1_ent_mentions), \
                           bcubed(graph2_ent_mentions, graph1_ent_mentions), \
                           ceaf(graph2_ent_mentions, graph1_ent_mentions)
    mela2 = np.mean([muc2, bcubed2, ceaf2])

    muc_score = np.mean([muc1, muc2])
    bcubed_score = np.mean([bcubed1, bcubed2])
    ceaf_score = np.mean([ceaf1, ceaf2])
    mela_score = np.mean([mela1, mela2])


    return muc_score, bcubed_score, ceaf_score, mela_score


def muc(gold_mentions, response_mentions):
    """
    M. Vilain, J. Burger, J. Aberdeen, D. Connolly, and L. Hirschman. 1995.
    A model theoretic coreference scoring scheme. In MUC-6.
    https://www.aclweb.org/anthology/M/M95/M95-1005.pdf

    The MUC measure focuses on the links (pairs of mentions) and computes recall and precision scores for each link.
    The recall is the number of common links between entities in K and R divided by the number of links in K.
    The precision is the number of common links between entities in K and R divided by the number of links in R.
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: The F1 score computed by MUC
    """
    gold_links = set([(x, y) for entity in gold_mentions for x in entity for y in entity if x != y])
    response_links = set([(x, y) for entity in response_mentions for x in entity for y in entity if x != y])

    # No links - both annotators decided to separate all mentions to different clusters
    if len(gold_links) == 0 and len(response_links) == 0:
        return 1.00

    intersection = gold_links.intersection(response_links)
    recall = len(intersection) / (1.0 * len(gold_links)) if len(gold_links) > 0 else 0.0
    precision = len(intersection) / (1.0 * len(response_links)) if len(response_links) > 0 else 0.0

    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return f1


def muc_micro(gold_mentions, response_mentions):
    """
    M. Vilain, J. Burger, J. Aberdeen, D. Connolly, and L. Hirschman. 1995.
    A model theoretic coreference scoring scheme. In MUC-6.
    https://www.aclweb.org/anthology/M/M95/M95-1005.pdf

    The MUC measure focuses on the links (pairs of mentions) and computes recall and precision scores for each link.
    The recall is the number of common links between entities in K and R divided by the number of links in K.
    The precision is the number of common links between entities in K and R divided by the number of links in R.
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: The F1 score computed by MUC
    """
    gold_links = set([(x, y) for entity in gold_mentions for x in entity for y in entity if x != y])
    response_links = set([(x, y) for entity in response_mentions for x in entity for y in entity if x != y])

    # No links - both annotators decided to separate all mentions to different clusters
    if len(gold_links) == 0 and len(response_links) == 0:
        return 1.00

    intersection = gold_links.intersection(response_links)
    recall_num = len(intersection)
    recall_den = len(gold_links)
    precision_num = len(intersection)
    precision_den = len(response_links)

    return recall_num,recall_den,precision_num,precision_den


def bcubed(gold_mentions, response_mentions):
    """
    Amit Bagga and Breck Baldwin. 1998.
    Algorithms for Scoring Coreference Chains. In LREC.
    http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.47.5848

    The B-CUBED metric focuses on the mentions and computes recall and precision scores for each mention.
    If K is the key entity containing mention M, and R is the response entity containing mention M, then recall for the
    mention M is computed as |K intersects R|/|K| and precision for the same is is computed as |K intersects R|/|R|.
    Overall recall and precision are the average of the individual mention scores.
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: The F1 score computed by B-CUBED
    """
    mention_to_entity_gold = { str(mention) : i for i, mention_set in enumerate(gold_mentions)
                               for mention in mention_set }
    mention_to_entity_response = { str(mention) : i for i, mention_set in enumerate(response_mentions)
                                   for mention in mention_set }

    per_mention_recall = []
    per_mention_precision = []

    # Compute the per mention recall and precision
    for mention in mention_to_entity_gold.keys():

        if mention not in mention_to_entity_response:
            continue

        K = set(gold_mentions[mention_to_entity_gold[mention]])
        R = set(response_mentions[mention_to_entity_response[mention]])
        intersection = K.intersection(R)
        per_mention_recall.append(len(intersection) / (1.0 * len(K)) if len(K) > 0 else 0.0)
        per_mention_precision.append(len(intersection) / (1.0 * len(R)) if len(R) > 0 else 0.0)

    recall, precision = np.mean(per_mention_recall), np.mean(per_mention_precision)

    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return f1


def bcubed_micro(gold_mentions, response_mentions):
    """
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: recall_num, recall_den, prec_num, prec_den
    """
    mention_to_entity_gold = { str(mention) : i for i, mention_set in enumerate(gold_mentions)
                               for mention in mention_set }
    mention_to_entity_response = { str(mention) : i for i, mention_set in enumerate(response_mentions)
                                   for mention in mention_set }

    per_mention_recall = []
    per_mention_precision = []

    # Compute the per mention recall and precision
    for mention in mention_to_entity_gold.keys():

        if mention not in mention_to_entity_response:
            continue

        K = set(gold_mentions[mention_to_entity_gold[mention]])
        R = set(response_mentions[mention_to_entity_response[mention]])
        intersection = K.intersection(R)
        per_mention_recall.append(len(intersection) / (1.0 * len(K)) if len(K) > 0 else 0.0)
        per_mention_precision.append(len(intersection) / (1.0 * len(R)) if len(R) > 0 else 0.0)

    recall, precision = np.sum(per_mention_recall), np.sum(per_mention_precision)

    # Follows CorScorer.pm line 626 from https://github.com/conll/reference-coreference-scorers
    # return recall, len(gold_mentions), precision, len(response_mentions)
    return recall, len(mention_to_entity_gold), precision, len(mention_to_entity_response)


def ceaf(gold_mentions, response_mentions):
    """
    Xiaoqiang Luo. 2005.
    On coreference resolution performance metrics. In HLT-EMNLP.
    http://www.aclweb.org/anthology/H05-1004

    The CEAF metric focuses on the entities and aligns every response entity with at most one key entity by finding the
    best one-to-one mapping between the entities using an entity similarity metric. This is a maximum bipartite matching
    problem and can be solved by the Kuhn-Munkres algorithm.
    Recall is the total similarity divided by the number of mentions in K, and precision is the total similarity
    divided by the number of mentions in R.
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: The F1 score computed by CEAF
    """

    recall_num, recall_den, precision_num, precision_den = ceaf_micro(gold_mentions, response_mentions)

    # Compute precision, recall and F1
    recall = recall_num / (1.0 * recall_den) if recall_den > 0 else 0.0
    precision = precision_num / (1.0 * precision_den) if precision_den > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return f1


def ceaf_micro(gold_mentions, response_mentions):
    """
    Xiaoqiang Luo. 2005.
    On coreference resolution performance metrics. In HLT-EMNLP.
    http://www.aclweb.org/anthology/H05-1004

    The CEAF metric focuses on the entities and aligns every response entity with at most one key entity by finding the
    best one-to-one mapping between the entities using an entity similarity metric. This is a maximum bipartite matching
    problem and can be solved by the Kuhn-Munkres algorithm.
    Recall is the total similarity divided by the number of mentions in K, and precision is the total similarity
    divided by the number of mentions in R.
    :param gold_mentions: a set of key entities, with each entity comprising one or more mentions
    :param response_mentions: a set of response entities, with each entity comprising one or more mentions
    :return: The F1 score computed by CEAF
    """

    # Compute the similarity between every entity (chain) in the key and response. Need to create a cost matrix
    # since Kuhn-Munkres finds minimal cost alignment and we are looking for maximal similarity
    similarities = np.vstack([np.array([entity_similarity(K, R) for K in gold_mentions]) for R in response_mentions])

    # The Munkres algorithm assumes that the cost matrix is square.
    # However, it's possible to use a rectangular matrix if you first pad it with 0 values to make it square.
    similarities = pad_to_square(similarities)

    # Find the optimal entity alignment with the Kuhn-Munkres algorithm
    m = Munkres()
    indices = m.compute(-similarities)
    total_cost = np.sum([similarities[row][col] for row, col in indices])

    # Compute entity self-similarity
    gold_self_similarity = np.sum([entity_similarity(K, K) for K in gold_mentions])
    response_self_similarity = np.sum([entity_similarity(R, R) for R in response_mentions])

    # Compute precision, recall and F1
    recall_num = total_cost
    recall_den = response_self_similarity
    precision_num = total_cost
    precision_den = gold_self_similarity
    return recall_num, recall_den, precision_num, precision_den


def entity_similarity(K, R):
    """
    The similarity metric for chains is based on how many common mentions two chains share (Luo, 2005):
    similarity  = 2 * |K intersects R|/ (|K| + |R|)
    :param K: an entity (set of mentions) from the key entities
    :param R: an entity (set of mentions) from the response entities
    :return: similarity  = 2 * |K intersects R|/ (|K| + |R|)
    """
    return 2.0 * len(K.intersection(R)) / (len(K) + len(R))


def pad_to_square(mat):
    """
    Pad a numpy array/matrix to be square
    :param mat: the numpy array
    :return: the padded matrix
    """
    new_m = mat

    # More rows than cols
    if mat.shape[0] > mat.shape[1]:
        new_m = np.hstack((new_m, np.zeros((mat.shape[0], mat.shape[0] - mat.shape[1]))))

    # More cols than cols
    elif mat.shape[1] > mat.shape[0]:
        new_m = np.vstack((new_m, np.zeros((mat.shape[1] - mat.shape[0], mat.shape[1]))))

    return new_m


def filter_clusters(graph, consensual_clusters):
    """
    Remove entities that are not consensual
    :param graph: the original graph
    :param consensual_clusters:
    :return: the graph, containing only the consensual clusters
    """

    consensual_graph = graph.clone()
    removed = []

    for entity_id, entity in consensual_graph.nodes.iteritems():

        if entity_id not in consensual_clusters.keys():
            removed.append(entity_id)
            continue

        # Filter mentions
        entity.mentions = { id : mention for id, mention in entity.mentions.iteritems()
                            if str(mention) in consensual_clusters[entity_id] }

        # Remove them also from the entailment graph
        entity.entailment.mentions_graph = [(m1, m2) for (m1, m2)
                                                  in entity.entailment.mentions_graph
                                                  if m1 in consensual_clusters[entity_id]
                                                  and m2 in consensual_clusters[entity_id]]

        # Remove entities without mentions
        if len(entity.mentions) == 0:
            removed.append(entity_id)

    # Remove entities without mentions
    consensual_graph.nodes = { entity_id : entity for entity_id, entity in consensual_graph.nodes.items()
                                  if entity_id not in removed }

    return consensual_graph
