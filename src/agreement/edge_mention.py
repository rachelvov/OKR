def debug(consensual_mentions, graph1_ent_mentions, graph2_ent_mentions):
	graph1_sents=set([m.split("[")[0] for m in graph1_ent_mentions])
	graph2_sents=set([m.split("[")[0] for m in graph2_ent_mentions])
	#print (graph1_sents-graph2_sents)
	delta1=graph1_ent_mentions-consensual_mentions
	delta1=[m for m in delta1 if m.split("[")[0] in graph2_sents]
	#print("graph1_edge_mentions-consensual_mentions:")
	#print delta1
	delta2=graph2_ent_mentions-consensual_mentions
	#print("graph2_edge_mentions-consensual_mentions:")
	#print delta2
	#print ("graph2_all:")
	#print graph2_ent_mentions


def compute_edge_mention_agreement(graph1, graph2):

	edges1=set([mention.toString(graph1) for edge in graph1.edges.values() for mention in edge.mentions.values()])
	edges2=set([mention.toString(graph2) for edge in graph2.edges.values() for mention in edge.mentions.values()])
	consensual_mentions=edges1.intersection(edges2)
	debug(consensual_mentions, edges1, edges2)
	accuracy1 = len(consensual_mentions) * 1.0 / len(edges1)
   	accuracy2 = len(consensual_mentions) * 1.0 / len(edges2)
	#edge_mention_acc = (accuracy1 + accuracy2) / 2 #for agreement
	edge_mention_acc=2.00*(accuracy1 *accuracy2)/(accuracy1 + accuracy2) #for gold and test

	consensual_graph1 = filter_mentions(graph1, consensual_mentions)
	consensual_graph2 = filter_mentions(graph2, consensual_mentions)

	return edge_mention_acc, consensual_graph1, consensual_graph2


def filter_mentions(graph, consensual_mentions):
    """
    Remove mentions that are not consensual
    :param graph: the original graph
    :param consensual_mentions: the mentions that both annotators agreed on
    :return: the graph, containing only the consensual mentions
    """

    consensual_graph = graph.clone()


    for edge in consensual_graph.edges.values():
        edge.mentions = {id: mention for id, mention in edge.mentions.iteritems()
                           if mention.toString(consensual_graph) in consensual_mentions}

        
        # Remove edges with no mentions
        if len(edge.mentions) == 0:
            consensual_graph.edges.pop(edge.id, None)
   
 
    return consensual_graph

