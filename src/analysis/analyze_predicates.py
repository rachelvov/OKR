""" Usage:
   analyze_predicates --in=GRAPHS_DIR

Analyzes different statistical properties of the graphs in the input directory.
Prints metrics to stdout.
"""
import sys
sys.path.append("../common")
from docopt import docopt
import logging
from okr import load_graphs_from_folder
import nltk
from collections import defaultdict
from operator import itemgetter

logging.basicConfig(level = logging.DEBUG)


class Predicate_analysis:
    """
    Run several metrics on a list of graphs
    """
    def __init__(self, graphs):
        """
        Initialize this instance with the graphs to analyze.
        """
        self.graphs = graphs

    def decide_main_pos(self, pos_list):
        """
        Decide what are the main pos tags.
        Currently does the following:
        1. Removes prepositions if noun, verbs or adjs exist in the pos_list (assumes they're auxiliary)
        """
        ret = pos_list
        if any([("VB" in pos) or ("NN" in pos) or ("JJ" in pos) for pos
                in map(itemgetter(1), pos_list)]):
            ret = filter(lambda (word, pos): pos != "IN",
                         pos_list)
        return ret

    def pos_distribution(self):
        """
        Calculate the POS distribution of the different word in each predicate
        """
        pos_dist = defaultdict(lambda: 0)
        for graph in self.graphs:
            for prop_id, prop in graph.propositions.iteritems():
                for prop_mention_id, prop_mention in prop.mentions.iteritems():
                    if not prop_mention.is_explicit:
                        # Count implicits differently
                        pos_dist["IMPL"] += 1
                        continue
                    sent_id = prop_mention.sentence_id
                    sent = graph.sentences[sent_id]
                    all_pos_tags = nltk.pos_tag(sent)
                    pred_pos_tags = [all_pos_tags[i] for i in prop_mention.indices]
                    for word, pos_tag in self.decide_main_pos(pred_pos_tags):
                        pos_dist[pos_tag] += 1

        consolidated_pos_dist = cnt_to_proportion(dict([(consolidated_pos,
                                                         sum([pos_dist[extended_pos]
                                                              for extended_pos in pos_dist.keys() if
                                                              consolidated_pos in extended_pos]))
                                                        for consolidated_pos
                                                        in ["VB", "NN", "JJ", "IN", "IMPL"]]))

        logging.info("POS dist: {}".format([(key, "{:.2f}".format(val))
                                            for key, val in sorted(consolidated_pos_dist.iteritems(),
                                                                   key = lambda (k, v): v,
                                                                   reverse = True)]))


        return pos_dist, consolidated_pos_dist


def cnt_to_proportion(d):
    """
    Transform a count dictionary to proportions.
    """
    total = sum(d.values())
    return dict([(key, float(val) / total) for key, val in d.iteritems()])

def analyze_predicates(graphs):
    """
    Run all predicate analyses on graphs
    """
    pa = Predicate_analysis(graphs)

    # POS:
    pa.pos_distribution()

if __name__ == "__main__":
    args = docopt(__doc__)
    graphs_dir = args['--in']

    # Load the annotation files to NLKG objects
    graphs = load_graphs_from_folder(graphs_dir)

    # Run analyses
    pa = Predicate_analysis(graphs)
    pos_dist, consolidated_pos_dist = pa.pos_distribution()
