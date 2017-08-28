import os
import sys
import itertools
sys.path.append('../common')
import spacy
import numpy as np
from spacy.en import English
import re
nlp = English()
def replace_tokenizer(nlp):
    old_tokenizer = nlp.tokenizer
    nlp.tokenizer = lambda string: old_tokenizer.tokens_from_list(string.split())

replace_tokenizer(nlp)

NOUNS=[u'NNP',u'NN', u'NNS', u'NNPS',u'CD',u'PRP',u'PRP$']
ADJECTIVES=[u'JJ',u'JJR',u'JJS']
VERBS=[u'VB', u'VBN', u'VBD', u'VBG', u'VBP']
S_WORDS=[u'IN',u'WDT',u'TO',u'DT']

from okr import *

class V2:
	def __init__(self, name,ignored_indices,nodes,edges, argument_alignment,sentences):
		self.name=name #object_name
       		self.ignored_indices = ignored_indices  # set of words to ignore, in format sentence_id[index_id]
		self.edges=edges #a dictionary of edge_id to edge 
		self.nodes=nodes #a dictionary of node_id to node
		self.argument_alignment=argument_alignment # a list of groups of edges aligned to same argument
		self.sentences=sentences #original sentences (same as in okr)
 	def clone(self):
       	 """
       	 Returns a deep copy of the graph
       	 """
       	 return copy.deepcopy(self)

		
class Node:
	def __init__(self, id, name, mentions, label,entailment):
		self.mentions=mentions #dictionary of mention_id to mention of node
		self.id=id #id of node- currenty "E+original_entity_id" or "P+original_proposition_id"
		self.name=name #name of node, the same as the name of original entity/proposition
		self.label=label #a set of all the mention terms of this node
		self.entailment=entailment #entailment graph for node (see entailment_graph object in okr)

class NodeMention:
	def __init__(self, id, sentence_id, indices, term, parent):
        	self.id = id #id of mention - same as in okr (an int)
        	self.sentence_id = sentence_id#sentence in which the mention appear
        	self.indices = indices #indices of the mention
       		self.term = term #words in the mention
        	self.parent = parent #id of the node to which the node mention belong
	def __str__(self):

        	return str(self.sentence_id) + str(self.indices)

class Edge:
	def __init__(self, id, nodes_pair):
		self.id=id #edge id - currently in the format of "Node_id_start_node+_+Node_id_end_node"
		self.nodes_pair=sorted(nodes_pair) #pair of nodes connected by edge
		self.mentions={} #dictionary of mention id to mention
		self.label=[]# set of all terms of all mentions


		

class EdgeMention:
	def __init__(self, id, nodes_mentions_pair,sentence_id, indices, terms,template):
		self.id = id #edge mention id - currently in the form of "original_proposition_id+_+original_mention_id" 
		self.nodes_mentions_pair=nodes_mentions_pair #the two nodes mentions connected by the edge mention
        	self.sentence_id = sentence_id #sentence of mention
        	self.indices = indices #indices of mention
       		self.terms = terms #terms of edge mention
       		self.template = template #template of edge mention
        	self.parent=[] #the edge in which the mention appear
	def __str__(self):

        	return str(self.sentence_id) + str(self.indices)


def to_letter(mention_type):
	if mention_type==1: #predicate
		return "P"
	else:
		return "E"

def change_template_predicate(template, terms, p_id):

	if terms==None or terms=="":
		#print ("as is: "+template+" "+p_id)
		return template
	template=" "+template+" "
	terms=" "+terms.lower()+" "
	#print(template+"\n")
	#print(terms+"\n")
	if template.find(terms)==-1:
		#print(p_id+": non-consecutive predicate:|"+terms+"| in the template: |"+template+"|")
		return template
		#TODO: handle
	#if len([n for n in re.finditer(terms, template)])>1:
		#print("terms found more than once"+terms+template)
	new_template=template.replace(terms," ["+str(p_id)+"] ")
	#print (new_template+"\n")
	return new_template
	
def change_template_arguments(template, arguments):
	#print(template)
	#print({a:b.parent_id for a,b in arguments.iteritems()})
	new_template=template
	for arg_id, arg in arguments.iteritems():
		arg_str="[a"+str(int(arg_id)+1)+"]"
		element = "E" if arg.mention_type==0 else "P"
		element_id="["+element+str(arg.parent_id)+"]"
		new_template=new_template.replace(arg_str,element_id)			
	#print (new_template)
	return new_template

def get_embedded_mentions(arguments):
	embedded={}
	for arg_id, arg in arguments.iteritems():
		if arg.mention_type==1: #embedded predicate
			element_id="P"+str(arg.parent_id)
			#print element_id
			embedded[element_id]=element_id+"_"+str(arg.parent_mention_id)
	#print embedded
	return embedded
		
def extract_nodes_from_templates(template):
	nodes=[]
	while template.find("[")>-1:
		start=template.find("[")
		end=template.find("]")
		node=template[start+1:end]
		nodes.append(node)
		template=template[end+1:]
	return nodes
		
	

def convert(okr):

	#entities to nodes:
	Entity_Nodes={}	
	for e_id,e in okr.entities.iteritems():
		new_entity_id="E"+str(e_id)
		mentions={m_id:NodeMention(m_id,m.sentence_id,m.indices,m.terms, new_entity_id) for m_id,m in e.mentions.iteritems()}
		Entity_Nodes[new_entity_id]=Node(new_entity_id,e.name, mentions, e.terms,e.entailment_graph)	

	#predicates to nodes:
	Proposition_Nodes={}
	Edges={}
	for p_id,p in okr.propositions.iteritems():

		#node id:
		new_p_id="P"+str(p_id)
		#get indices, words and pos for every predicate mention:
		prop_mentions={m_num:[[num,pos.orth_,pos.tag_] for num,pos in enumerate(nlp(unicode(" ".join(okr.sentences[m.sentence_id])))) if num in m.indices] for m_num,m in p.mentions.iteritems() if m.is_explicit} 
		#remove stop words from predicates:
		new_terms={m_num:" ".join([str(word[1]) for word in m if word[2] not in S_WORDS])for m_num,m in prop_mentions.iteritems()}
		new_indices={m_num:[word[0] for word in m if word[2] not in S_WORDS ]for m_num,m in prop_mentions.iteritems()}
		#set of predicate terms (for the label):
		new_terms_all=set([m for m in new_terms.values()])
		#convert predicate mentions to node mentions
		new_mentions={m_num: NodeMention(m_num,m.sentence_id,new_indices[m_num],new_terms[m_num], new_p_id) for m_num,m   in p.mentions.iteritems() if m.is_explicit}
		if (not (len(new_terms_all)==1 and [n for n in new_terms_all][0]=="")) and len(new_terms_all)>0:#not empty predicate
			Proposition_Nodes[new_p_id]=Node(new_p_id,p.name, new_mentions, new_terms_all,p.entailment_graph)
	
	#propositions to edges:
		#get indices and terms for explicit mentions:
		new_edge_indices={m_num:[word[0] for word in m if word[2] in S_WORDS ]for m_num,m in prop_mentions.iteritems()}
		new_edge_terms={m_num:" ".join([str(word[1]) for word in m if word[2] in S_WORDS]) for m_num,m in prop_mentions.iteritems()}
		content_word_mentions=[m_num for m_num,term in new_terms.iteritems() if not term==""]
		for mention_id,mention in p.mentions.iteritems():
			#get all arguments mentions:
			arguments_mentions={arg_id:(to_letter(arg.mention_type)+str(arg.parent_id), arg.parent_mention_id) for arg_id,arg in mention.argument_mentions.iteritems()}
			if mention_id in content_word_mentions:# mention with a content word predicate
				predicate_mention=[new_p_id, mention_id]
				#get all predicate-argument mention pairs:
				mention_pairs=[[predicate_mention, arg_men] for arg_men in arguments_mentions.values() ]
			else: #implicit or non-content-word predicate:
				mention_pairs=list(itertools.combinations(arguments_mentions.values(), 2))
			#create edge mention for every ,mention pair:
			edge_mention_id=str(p_id)+"_"+str(mention_id)
			sentence_id=mention.sentence_id	
			new_edge_template_pred=change_template_predicate(mention.template,new_terms.get(mention_id, None),new_p_id)
			new_edge_template=change_template_arguments(new_edge_template_pred,mention.argument_mentions) 
			indices=new_edge_indices.get(mention_id,None) #if no stop-words in edge template, return None
			terms=new_edge_terms.get(mention_id, None) #if no stop-words in edge template, return None
			for pair in mention_pairs:
				#create edge mention:	
				edge_mention=EdgeMention(edge_mention_id,sorted(pair),sentence_id, indices, terms,new_edge_template)
				#insert into correct edge:
				nodes_pair=sorted([p[0] for p in pair]) #the pair of nodes (without mentions)
				edge_id="_".join(nodes_pair)
				if edge_id not in Edges: #create edge
					Edges[edge_id]=Edge(edge_id,nodes_pair)
				Edges[edge_id].mentions[edge_mention_id]=edge_mention
				edge_mention.parent=edge_id						
	Nodes={}
	Nodes.update(Entity_Nodes)
	Nodes.update(Proposition_Nodes)		
				
	
	#Add argument alinment links:
	Args={}
	Argument_Alignment={}
	for p_id,p in okr.propositions.iteritems():
		new_p_id="P"+str(p_id)
		Args[new_p_id]={}
		for m in p.mentions.values():
			 for a_id,a in m.argument_mentions.iteritems():
				element = "E" if a.mention_type==0 else "P"
				element_id=element+str(a.parent_id)
				if a_id not in Args[new_p_id]:
					Args[new_p_id][a_id]=set()
		 		Args[new_p_id][a_id].add(element_id)
		alignment=[[new_p_id+"_"+element for element in v] for k,v in Args[new_p_id].iteritems() if len(v)>1 ]
		if (len(alignment)>0):
			Argument_Alignment[new_p_id]=alignment
	
	#create final V2 object:
	v2=V2(okr.name,okr.ignored_indices,Nodes,Edges, Argument_Alignment, okr.sentences)
	return v2		

def main():	

	input_file=sys.argv[1]
	okr = load_graph_from_file(input_file)
	v2=convert(okr)	

if __name__ == '__main__':
   main()
