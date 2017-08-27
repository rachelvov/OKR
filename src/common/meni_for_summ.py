import sys
from okr import *
from V2Conversion import *
from collections import defaultdict
import re
from collections import Counter
from datetime import *
from itertools import groupby

def add_counts(list_): #adds counts in [] brackets to values in list
	return [k+"["+str(v)+"]" for k,v in Counter(list_).iteritems()]

def add_counts_tweets(list_): #adds counts and tweet numbers in [] brackets to values in list (contating [template,sent_id])
	#sort by template:
	list_.sort(key=lambda x:x[0])
	#group by template:
	list_sorted=[[k,[sent_to_tweet[i[1]] for i in g]] for k,g in groupby(list_, lambda x: x[0])]
	return [t[0]+"["+str(len(t[1]))+","+",".join(t[1])+"]" for t in list_sorted]


def get_earliest_date(edge): #gets earliest date for each proposition
	tweet_ids=[sent_to_tweet[m.sentence_id] for m in edge.mentions.values()]
	if len([t for t in tweet_ids if t not in tweet_data])>5:
		print "many missing tweets!"
	return str(min([tweet_data[tweet_id]["time"] for tweet_id in tweet_ids if tweet_id in tweet_data]))

def brackets(string_a): #change brackets to <> and add proposition number, change ";" to ","
	string_a= string_a.replace("[","<").replace("]",">").replace(";",",")
	return string_a


file_name=sys.argv[1]
data_file_name=sys.argv[2]
#id to tweet data dictionary: 
tweet_data={line.split("\t")[0]:{"screen_name":line.split("\t")[1],
				 "user_id": line.split("\t")[2],					
				 "time": datetime.strptime(line.split("\t")[3].strip()	,"%Y-%m-%d %H:%M:%S")} 
								for line in open(data_file_name,"r").readlines()}

nlkg=load_graph_from_file(file_name)
v2=convert(nlkg)
#nlkg=None
file_name=nlkg.name[nlkg.name.rfind("/")+1:]
sent_to_tweet=nlkg.tweet_ids

if len(sys.argv)>3:
	ids_file=sys.argv[3]
	sent_to_tweet.update({int(line.split("\t")[0]):line.split("\t")[1].strip() for line in open(ids_file,"r").readlines()})
#check that tweet ids were updated:
if len(sent_to_tweet)==0:
	print "Error: no tweet ids in xml file or input file"
	sys.exit()
output_file=open(file_name+".txt","w")
#file name:
output_file.write(file_name+"\n\n")
#Nodes:
output_file.write('#Nodes\n\n')
for node in v2.nodes.values():
	#add counts:
	terms=add_counts([mention.term for mention in node.mentions.values()])
	output_file.write(node.name+"\t"+"\t".join(terms)+";\n")

output_file.write('#Edges\n\n')
#print propositions:

for key,edge in v2.edges.iteritems():
	output_file.write("#Edge"+str(key)+"\t"+str(get_earliest_date(edge)))
	#if edge.attributor is not None:
		#output_file.write("\tAttributor: "+ nlkg.entities[int(proposition.attributor)].name)
	output_file.write("\n\n")
	output_file.write("#labels\n\n")
	#switch brackets+add proposdition number+treat implicit in templates:
	new_proposition_templates=[(brackets(a.template) if a.is_explicit else "IMPLICIT",a.sentence_id)  for a in edge.mentions.values()]
	#add counts+change name of implicit+add tweets numbers: 
	counted_templates=add_counts_tweets(new_proposition_templates)
	#switch brackets in entailment+ remove templates not appearing in propositions (TODO: fix bug that causes it)
	#new_entailment_graph=[(brackets(pair[0],key),brackets(pair[1],key)) for pair in proposition.entailment_graph.graph if brackets(pair[0],key) in new_proposition_templates and brackets(pair[1],key) in new_proposition_templates]
	output_file.write("\t".join(counted_templates)+";\n\n")
	#print arguments:
	output_file.write("#arguments\n\n")
	all_nodes=set([node for mention in edge.mentions.values() for node in mention.all_nodes])
	all_nodes_details1=[(v2.nodes[node],set([ sent_to_tweet[m.sentence_id] for m in v2.nodes[node].mentions.values()])) for node in all_nodes]
	all_nodes_details2=[node[0].id+"\t"+node[0].name+"\t["+str(len(node[1]))+","+",".join(node[1])+"]" for node in all_nodes_details1]
	
	output_file.write("\n".join(all_nodes_details2)+"\n\n")
	
	

output_file.close()



