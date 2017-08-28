import os
import sys
import collections
sys.path.append('../common')
import numpy as np
from okr import *
from V2_conversion2 import *

def strip_predicate(pred_string):
	pred_string=unicode(pred_string, "utf-8")
	return " ".join([word.lemma_ for word in nlp(pred_string) if (not word.is_stop) and (not word.tag_==u'IN')])



if (not len(sys.argv)==2):
	print("please run:  python V2_analysis.py ../../data/All")
data_dir = sys.argv[1]
files = sorted(os.listdir(data_dir))
all_graphs = [convert(load_graph_from_file(data_dir+'/'+file1)) for file1 in files]

number_of_nodes=sum([len(graph.nodes) for graph in all_graphs])
print("number_of_nodes: "+ str(number_of_nodes))
number_of_singelton_nodes=sum([len([node for node in graph.nodes.values() if len(node.mentions)==1]) for graph in all_graphs])
number_of_chains_nodes=sum([len([node for node in graph.nodes.values() if len(node.mentions)>1]) for graph in all_graphs])
print ("number_of_singelton_nodes: "+ str(number_of_singelton_nodes))
print ("number_of_chains_nodes: "+ str(number_of_chains_nodes))

all_node_mentions=sum([len(node.mentions) for graph in all_graphs for node in graph.nodes.values()])
print ("number_of_nodes_mentions: "+ str(all_node_mentions))
number_of_singelton_nodes_m=sum([len(node.mentions) for graph in all_graphs for node in graph.nodes.values() if len(node.mentions)==1])
number_of_chains_nodes_m=sum([len(node.mentions) for graph in all_graphs for node in graph.nodes.values() if len(node.mentions)>1])
print ("number_of_singelton_nodes_mentions: "+ str(number_of_singelton_nodes_m))
print ("number_of_chains_nodes_mentions: "+ str(number_of_chains_nodes_m))
average_number_of_node_terms=np.average([len(set([strip_predicate(m.term) for m in node.mentions.values()]))for graph in all_graphs for node in graph.nodes.values() if len(node.mentions)>1 ])
print ("average_number_of_node_terms: "+ str(average_number_of_node_terms))

number_of_edges=sum([len(graph.edges) for graph in all_graphs])
print("number_of_edges: "+ str(number_of_edges))
number_of_singelton_edges=sum([len([edge for edge in graph.edges.values() if len(edge.mentions)==1]) for graph in all_graphs])
number_of_chains_edges=sum([len([edge for edge in graph.edges.values() if len(edge.mentions)>1]) for graph in all_graphs])
print ("number_of_singelton_edges: "+ str(number_of_singelton_edges))
print ("number_of_chains_edges: "+ str(number_of_chains_edges))

all_edge_mentions=sum([len(edge.mentions) for graph in all_graphs for edge in graph.edges.values()])
print ("number_of_edge_mentions: "+ str(all_edge_mentions))
number_of_singelton_edges_m=sum([len(edge.mentions) for graph in all_graphs for edge in graph.edges.values() if len(edge.mentions)==1])
number_of_chain_edges_m=sum([len(edge.mentions) for graph in all_graphs for edge in graph.edges.values() if len(edge.mentions)>1])
print ("number_of_singelton_edges_mentions: "+ str(number_of_singelton_edges_m))
print ("number_of_chains_edges_mentions: "+ str(number_of_chain_edges_m))
average_number_of_edge_terms=np.average([len(set([strip_predicate(m.terms) for m in edge.mentions.values()]))for graph in all_graphs for edge in graph.edges.values() if len(edge.mentions)>1 ])
print ("average_number_of_edge_terms: "+ str(average_number_of_edge_terms))

nodes_of_edges=[graph.name+edge.start_node for graph in all_graphs for edge in graph.edges.values()]
nodes_of_edges+=[graph.name+edge.end_node for graph in all_graphs for edge in graph.edges.values()]
number_of_edges_per_node=collections.Counter(nodes_of_edges)
average_number_of_edges_per_node=1.00*sum([v for v in number_of_edges_per_node.values()])/len(number_of_edges_per_node)
print ("average_number_of_edges_per_node: "+ str(average_number_of_edges_per_node))

