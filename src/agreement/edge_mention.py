def compute_edge_mention_agreement(graph1, graph2):

	edges1=set(edge_mentions(graph1))
	edges2=set(edge_mentions(graph2))
	consensual_mentions=edges1.intersection(edges2)
	accuracy1 = len(consensual_mentions) * 1.0 / len(edges1)
   	accuracy2 = len(consensual_mentions) * 1.0 / len(edges2)
	edge_mention_acc = (accuracy1 + accuracy2) / 2

	return(edges1, edges2,edge_mention_acc)

def edge_mentions(graph):
	all_edge_mentions=[]
	for edge in graph.edges.values():
		start_node_strs=[(str(mention),mention.sentence_id) for mention in graph.nodes[edge.start_node].mentions.values()]
		end_node_strs=[(str(mention),mention.sentence_id) for mention in graph.nodes[edge.end_node].mentions.values()]
        	all_edge_mentions.append([(min(x[0],y[0]),max(x[0],y[0])) for x in start_node_strs for y in end_node_strs if x[1]==y[1]] )
	return [pair for edge_pairs in all_edge_mentions for pair in edge_pairs]

