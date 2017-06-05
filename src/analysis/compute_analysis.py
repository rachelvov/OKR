""" Usage:
    compute_analysis <graphs_folder>

    Receives a graphs file and print statistical data analytics:
    1) Predicate POS distribution
    2) Entailment analysis
"""

import sys

sys.path.append("../common")

from okr import *
from docopt import docopt
import logging
logging.basicConfig(level = logging.INFO)

from analyze_entities import *
from analyze_predicates import analyze_predicates
from analyze_entailment_graphs import analyze_entailment

def run_analysis(graphs):
    """
    Run all of the avilable analyses on graphs

    """
    # Entities
    analyze_entities(graphs)
	
    # Predicates
    analyze_predicates(graphs)

    # Entailment
    analyze_entailment(graphs)

if __name__ == "__main__":
    args = docopt(__doc__)
    graphs_dir = args['<graphs_folder>']

    # Load the annotation files to NLKG objects
    graphs = load_graphs_from_folder(graphs_dir)

    run_analysis(graphs)
