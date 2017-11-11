import os
import sys
sys.path.append('../common')

import numpy as np

from okr import *
from V2Conversion import *
from node_coref import compute_node_coref_agreement
from edge_mention import compute_edge_mention_agreement
from node_mention import compute_node_mention_agreement
from edge_coref import compute_edge_coref_agreement

def compute_agreement(file1,file2):
	# Load the annotation files to V2 objects
	graph1 = convert(load_graph_from_file(file1))
	graph2 = convert(load_graph_from_file(file2))
	return compute_agreement_graphs(graph1,graph2)

def compute_agreement_graphs(graph1,graph2):
	# Load the annotation files to V2 objects
	node_mention_acc, consensual_graph1, consensual_graph2=compute_node_mention_agreement(graph1, graph2)
	print 'Node mentions: %.3f' % node_mention_acc
	edge_mention_acc, consensual_graph1, consensual_graph2=compute_edge_mention_agreement(consensual_graph1, consensual_graph2)
	print 'Edge mentions: %.3f' % edge_mention_acc
	ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1 = \
        compute_node_coref_agreement(consensual_graph1, consensual_graph2)
	print 'Node coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % (ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1)
	edge_muc, edge_b_cube, edge_ceaf_c, edge_conll_f1 = \
        compute_edge_coref_agreement(consensual_graph1, consensual_graph2)
	print 'edge coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % (edge_muc, edge_b_cube, edge_ceaf_c, edge_conll_f1)

	return node_mention_acc,edge_mention_acc,ent_muc, ent_b_cube, ent_ceaf_c, ent_conll_f1,edge_muc, edge_b_cube, edge_ceaf_c, edge_conll_f1


def main():
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
    node_score, edge_score, ent_muc, ent_b_cube, ent_ceaf_c, ent_mela,edge_muc, edge_b_cube, edge_ceaf_c, edge_conll_f1 = average.tolist()

    print '\n\nAverage:\n=========\n'
    print 'Node mentions: %.3f' % node_score
    print 'Edge mentions: %.3f' % edge_score
    print 'Node coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % \
          (ent_muc, ent_b_cube, ent_ceaf_c, ent_mela)
    print 'edge coreference: MUC=%.3f, B^3=%.3f, CEAF_C=%.3f, MELA=%.3f' % (edge_muc, edge_b_cube, edge_ceaf_c, edge_conll_f1)



if __name__ == '__main__':
    main()
