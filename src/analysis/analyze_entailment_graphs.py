"""
analyze_entailment_graph
Author: Vered Shwartz

    Receives a directory of annotated files, and prints, for each {entities, predicates, arguments}:
    1) % of graphs that are not connected
    2) qualitative examples for such graphs
"""

import sys

sys.path.append("../common")

from okr import *
from docopt import docopt


def analyze_entailment(okrs):
    """
    Receives a directory of annotated files, and prints, for each {entities, predicates, arguments}:
    1) % of graphs that are not connected
    2) qualitative examples for such graphs
    """
    examples = [[], []]
    per_not_connected = [0, 0]
    descriptions = ['Entity', 'Proposition']

    for okr in okrs:

        mention_by_key = [okr.ent_mentions_by_key, okr.prop_mentions_by_key]

        for item_index, items in enumerate([okr.entities.values(), okr.propositions.values()]):

            num_not_connected = 0
            explicit_items = 0

            for item in items:
                mentions = [str(m) for m in item.mentions.values() if item_index == 0 or m.is_explicit]

                if len(mentions) == 0:
                    continue

                explicit_items += 1

                mention_to_index = { m : i for i, m in enumerate(mentions) }
                adjacency_list = { mention_to_index[m] :
                                       set([mention_to_index[m2] for (m1, m2) in
                                            item.entailment_graph.mentions_graph if m1 == m] +
                                           [mention_to_index[m1] for (m1, m2) in
                                            item.entailment_graph.mentions_graph if m2 == m])
                                   for m in mentions }

                # Add an edge from each node to all the nodes with the same text
                adjacency_list = { m : neighbours.union([mention_to_index[m_other] for m_other in mentions
                                                         if mention_by_key[item_index][mentions[m]].terms ==
                                                         mention_by_key[item_index][m_other].terms])
                                   for m, neighbours in adjacency_list.iteritems() }

                connected_components = get_connected_components(adjacency_list)

                if len(connected_components) > 1:
                    num_not_connected += 1

                    connected_components_str = [ [mention_by_key[item_index][mentions[mention_index]]
                                                  for mention_index in component]
                                                 for component in connected_components ]

                    examples[item_index].append(connected_components_str)

            per_not_connected[item_index] += (num_not_connected * 1.0) / explicit_items

    for item_index in range(2):
        print '%s: %.2f' % (descriptions[item_index], (per_not_connected[item_index] * 1.0) / len(okrs) * 100) + '%'
        print 'Examples:'
        for example in examples[item_index]:
            print [[m.terms for m in component] for component in example]
        print



def main():
    """
    Receives a directory of annotated files, and prints, for each {entities, predicates, arguments}:
    1) % of graphs that are not connected
    2) qualitative examples for such graphs
    """
    args = docopt("""Receives a directory of annotated files, and prints, for each {entities, predicates, arguments}:
    1) % of graphs that are not connected
    2) qualitative examples for such graphs

    Usage:
        analyze_entailment_graph.py <annotations_dir>
    """)

    annotations_dir = args['<annotations_dir>']

    # Load the annotation files to NLKG objects
    okrs = load_graphs_from_folder(annotations_dir)
    analyze_entailment(okrs)


def get_connected_components(graph):
    """
    Receives a graph represented as an adjacency list and returns the connected components in the graph.
    :param nodes: the graph (adjacency list)
    :return: the connected components in the graph
    """
    components = []
    nodes = set(graph.keys())

    # There are still unvisited nodes
    while len(nodes) > 0:

        # Start with a random node
        curr_node = nodes.pop()

        # Start a new connected component
        curr_component = [curr_node]
        nodes_to_visit = [curr_node]

        # Add the neighbors of the current node to the list of nodes to visit.
        # When there are no more neighbors to visit, we finished visiting all the nodes in this connected component.
        while len(nodes_to_visit) > 0:

            curr_node = nodes_to_visit.pop()

            # Get the neighbors
            neighbors = set([neighbor for neighbor in graph[curr_node]])

            # Remove the neighbors we already visited from the current neighbors and from the node list,
            # and add them to the current connected component
            neighbors.difference_update(curr_component)
            nodes.difference_update(neighbors)
            curr_component.extend(neighbors)
            curr_component = list(set(curr_component))

            # Add them to the queue, so we visit them in the next iterations
            nodes_to_visit.extend(neighbors)

        components.append(curr_component)

    return components


if __name__ == '__main__':
    main()
