import os
import sys
sys.path.append('../common')

import numpy as np

from okr import *
from V2Conversion import *
from node_coref import compute_node_coref_agreement
from edge_mention import compute_edge_mention_agreement
from node_mention import compute_node_mention_agreement
from argument_coref import compute_argument_coref_agreement
from predicate_coref import compute_predicate_coref_agreement
from entailment_graph import compute_entailment_graph_agreement
from argument_mention import compute_argument_mention_agreement
from predicate_mention import compute_predicate_mention_agreement, compute_predicate_mention_agreement_verbal, \
    compute_predicate_mention_agreement_non_verbal


def compute_agreement(file1,file2):
	# Load the annotation files to V2 objects
	graph1 = convert(load_graph_from_file(file1))
	graph2 = convert(load_graph_from_file(file2))
	node_mention_acc, consensual_graph1, consensual_graph2=compute_node_mention_agreement(graph1, graph2)
	print 'Node mentions: %.3f' % node_mention_acc
	edges1, edges2,edge_mentions_acc=compute_edge_mention_agreement(consensual_graph1, consensual_graph2)
	print 'Edge mentions: %.3f' % edge_mentions_acc
	ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1, consensual_graph1, consensual_graph2 = \
        compute_node_coref_agreement(consensual_graph1, consensual_graph2)
	print 'Node coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % (ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1)
	return node_mention_acc,edge_mentions_acc,ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1

#def main():
if 1==1:
    if (not len(sys.argv)==3):
	print("please run:  python compute_agreement_v2.py ../../data/agreement/annotator_1 ../../data/agreement/annotator_2")

    annotator1_dir = sys.argv[1]
    annotator2_dir = sys.argv[2]

    annotator1_files = sorted(os.listdir(annotator1_dir))
    annotator2_files = sorted(os.listdir(annotator2_dir))

    results = []
    for annotator1_file, annotator2_file in zip(annotator1_files, annotator2_files):
        print 'Agreement for %s, %s' % (annotator1_dir + '/' + annotator1_file, annotator2_dir + '/' + annotator2_file)
        results.append(compute_agreement(annotator1_dir + '/' + annotator1_file, annotator2_dir + '/' + annotator2_file))
    average = np.mean(results, axis=0)
    node_score, edge_score, ent_muc, ent_b_cube, ent_ceaf_c, ent_mela = average.tolist()

    print '\n\nAverage:\n=========\n'
    print 'Node mentions: %.3f' % node_score
    print 'Edge mentions: %.3f' % edge_score
    print 'Node coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % \
          (ent_muc, ent_b_cube, ent_ceaf_c, ent_mela)


#if __name__ == '__main__':
#    main()
