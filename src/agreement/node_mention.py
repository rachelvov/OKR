"""
Author: Rachel Wities and Vered Shwartz

    Receives two annotated graphs and computes the agreement on the node mentions.
    We average the accuracy of the two annotators, each computed while taking the other as a gold reference.
"""
import sys

sys.path.append('../common')

from mention_common import *

def debug(consensual_mentions, graph1_ent_mentions, graph2_ent_mentions):
	graph1_sents=set([m.split("[")[0] for m in graph1_ent_mentions])
	graph2_sents=set([m.split("[")[0] for m in graph2_ent_mentions])

	delta1=graph1_ent_mentions-consensual_mentions
	delta1=[m for m in delta1 if m.split("[")[0] in graph2_sents]
	
	delta2=graph2_ent_mentions-consensual_mentions
	


def compute_node_mention_agreement(graph1, graph2):
    """
    Compute node mention agreement on two graphs
    :param graph1: the first annotator's graph
    :param graph2: the second annotator's graph
    :return node mention accuracy and the consensual graphs
    """

    # Get the consensual mentions and the mentions in each graph
    consensual_mentions, graph1_ent_mentions, graph2_ent_mentions = extract_consensual_mentions(graph1, graph2)
    debug(consensual_mentions, graph1_ent_mentions, graph2_ent_mentions)
    # Compute the accuracy, each time taking one annotator as the gold
    accuracy1 = len(consensual_mentions) * 1.0 / len(graph1_ent_mentions)
    accuracy2 = len(consensual_mentions) * 1.0 / len(graph2_ent_mentions)

    #node_mention_acc = (accuracy1 + accuracy2) / 2 #for agreement
    node_mention_acc = 2.00*(accuracy1 *accuracy2)/(accuracy1 + accuracy2) #for gold and test

    consensual_graph1 = filter_mentions(graph1, consensual_mentions)
    consensual_graph2 = filter_mentions(graph2, consensual_mentions)

    return node_mention_acc, consensual_graph1, consensual_graph2


def filter_mentions(graph, consensual_mentions):
    """
    Remove mentions that are not consensual
    :param graph: the original graph
    :param consensual_mentions: the mentions that both annotators agreed on
    :return: the graph, containing only the consensual mentions
    """

    consensual_graph = graph.clone()


    for node in consensual_graph.nodes.values():
        node.mentions = {id: mention for id, mention in node.mentions.iteritems()
                           if str(mention) in consensual_mentions}

        # Remove them also from the entailment graph
        #node.entailment.mentions_graph = [(m1, m2) for (m1, m2) in node.entailment.mentions_graph
        #                                          if m1 in consensual_mentions and m2 in consensual_mentions]

        # Remove nodes with no mentions
        if len(node.mentions) == 0:
            consensual_graph.nodes.pop(node.id, None)
    #remove edges with one missing node:
    for edge in consensual_graph.edges.values():
	if edge.nodes_pair[0] not in  consensual_graph.nodes or edge.nodes_pair[1] not in  consensual_graph.nodes:
	    consensual_graph.edges.pop(edge.id, None)

    #remove edge mentions  with one missing node:
    for edge in consensual_graph.edges.values():
      edge.mentions = {id: mention for id, mention in edge.mentions.iteritems()
                           if mention.toString(graph).split("_")[0] in consensual_mentions and mention.toString(graph).split("_")[1] in consensual_mentions }
    #remove empty edges:
      if len(edge.mentions) == 0:
            consensual_graph.edges.pop(edge.id, None)
   

 
    return consensual_graph


def extract_consensual_mentions(graph1, graph2):
    """
    Receives two graphs, and returns the consensual node mentions, and the node mentions in each graph.
    :param graph1: the first annotator's graph
    :param graph2: the second annotator's graph
    :return the consensual node mentions, and the node mentions in each graph
    """

    # Get the node mentions in both graphs
    graph1_ent_mentions = set.union(*[set(map(str, node.mentions.values())) for node in graph1.nodes.values() ])
    graph2_ent_mentions = set.union(*[set(map(str, node.mentions.values())) for node in graph2.nodes.values() ])

    # Exclude sentence that weren't anotated by both:
    common_sentences = set([x.split('[')[0] for x in graph1_ent_mentions]).intersection(
        set([x.split('[')[0] for x in graph2_ent_mentions]))
    graph1_ent_mentions = set([a for a in graph1_ent_mentions if a.split('[')[0] in common_sentences])
    graph2_ent_mentions = set([a for a in graph2_ent_mentions if a.split('[')[0] in common_sentences])

    # Exclude ignored_words, for versions 5 and up:
    if not graph2.ignored_indices == None:
        graph1_ent_mentions = set([a for a in graph1_ent_mentions if len(overlap_set(a, graph2.ignored_indices)) == 0])

    if not graph1.ignored_indices == None:
        graph2_ent_mentions = set([a for a in graph2_ent_mentions if len(overlap_set(a, graph1.ignored_indices)) == 0])

    consensual_mentions = graph1_ent_mentions.intersection(graph2_ent_mentions)

    return consensual_mentions, graph1_ent_mentions, graph2_ent_mentions
