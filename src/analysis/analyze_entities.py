import sys
import spacy
nlp = spacy.load('en')
import numpy as np
NOUNS=[u'NNP',u'NN', u'NNS', u'NNPS',u'CD',u'PRP',u'PRP$']
ADJECTIVES=[u'JJ',u'JJR',u'JJS']
VERBS=[u'VB', u'VBN', u'VBD', u'VBG', u'VBP']
from collections import Counter


def strip_predicate(pred_string):
	pred_string=unicode(pred_string, "utf-8")
	return " ".join([word.lemma_ for word in nlp(pred_string) if (not word.is_stop) and (not word.tag_==u'IN')])

def is_explicit(proposition):
	expl_mentions=[m for m in proposition.mentions.values() if m.is_explicit]
	return len(expl_mentions)>0	
def fix_bug(string_):	
	return string_.replace("-","~").replace("'","|")




def analyze_entities(all_events):
	#numbers of entities:
	number_of_entities=sum([len(graph.entities) for graph in all_events])
	print("number_of_entities: "+ str(number_of_entities))
	number_of_singelton_entities=sum([len([entity for entity in graph.entities.values() if len(entity.mentions)==1]) for graph in all_events])
	number_of_chains_entities=sum([len([entity for entity in graph.entities.values() if len(entity.mentions)>1]) for graph in all_events])
	print ("number_of_singelton_entities: "+ str(number_of_singelton_entities))
	print ("number_of_chains_entities: "+ str(number_of_chains_entities))

	all_ent_mentions=sum([len(entity.mentions) for graph in all_events for entity in graph.entities.values()])
	print ("number_of_entities mentions: "+ str(all_ent_mentions))
	number_of_singelton_entities_m=sum([len(entity.mentions) for graph in all_events for entity in graph.entities.values() if len(entity.mentions)==1])
	number_of_chains_entities_m=sum([len(entity.mentions) for graph in all_events for entity in graph.entities.values() if len(entity.mentions)>1])
	print ("number_of_singelton_entities_mentions: "+ str(number_of_singelton_entities_m))
	print ("number_of_chains_entities_mentions: "+ str(number_of_chains_entities_m))
	average_number_of_ent_terms=np.average([len(set([strip_predicate(m.terms) for m in entity.mentions.values()]))for graph in all_events for entity in graph.entities.values() if len(entity.mentions)>1 ])
	print ("average_number_of_ent_terms: "+ str(average_number_of_ent_terms))


	#numbers	 of propositions:
	number_of_propositions=sum([len(graph.propositions) for graph in all_events])
	print("number_of_props: "+ str(number_of_propositions))
	number_of_singelton_propositions=sum([len([proposition for proposition in graph.propositions.values() if len(proposition.mentions)==1]) for graph in all_events])
	number_of_chains_propositions=sum([len([proposition for proposition in graph.propositions.values() if len(proposition.mentions)>1]) for graph in all_events])
	print ("number_of_singelton_propositions: "+ str(number_of_singelton_propositions))
	print ("number_of_chains_propositions: "+ str(number_of_chains_propositions))

	all_prop_mentions=sum([len(proposition.mentions) for graph in all_events for proposition in graph.propositions.values()])
	print ("number_of_propositions_m: "+ str(all_prop_mentions))
	number_of_singelton_propositions_m=sum([len(proposition.mentions) for graph in all_events for proposition in graph.propositions.values() if len(proposition.mentions)==1])
	number_of_chains_propositions_m=sum([len(proposition.mentions) for graph in all_events for proposition in graph.propositions.values() if len(proposition.mentions)>1])
	print ("number_of_singelton_propositions_m: "+ str(number_of_singelton_propositions_m))
	print ("number_of_chains_propositions_m: "+ str(number_of_chains_propositions_m))
	number_of_expl_chain_propositions=len([proposition for graph in all_events for proposition in graph.propositions.values() if is_explicit(proposition) and len(proposition.mentions)>1])
	print ("number_of_expl_chain_propositions: "+ str(number_of_expl_chain_propositions) )

	number_of_expl_chain_propositions_m=sum([len([m for m in proposition.mentions.values() if m.is_explicit]) for graph in all_events for proposition in graph.propositions.values() if len(proposition.mentions)>1])
	print ("number_of_expl_chain_propositions_m: "+ str(number_of_expl_chain_propositions_m))
	average_number_of_prop_expl_terms=np.average([len(set([strip_predicate(m.terms) for m in proposition.mentions.values()]))for graph in all_events for proposition in graph.propositions.values() if len(proposition.mentions)>1 and is_explicit(proposition)])
	print ("average_number_of_prop_expl_terms: "+ str(average_number_of_prop_expl_terms))
	
	#analyze POS:
	entities_pos=[]	
	for graph in all_events:
		#load sentences:
		sents= {num:unicode(fix_bug(" ".join(sentence)), "utf-8") for num,sentence in graph.sentences.iteritems()}
		sents={key:sentence for key,sentence in sents.iteritems() if len(nlp(sentence))==len(graph.sentences[key])}
		new_mentions=[m for e in graph.entities.values() for m in e.mentions.values() if m.sentence_id in sents]
		curr_entities_pos=[pos.tag_ for m in new_mentions for num,pos in enumerate(nlp(sents[m.sentence_id])) if m.sentence_id in sents and num in m.indices]
		#curr_entities_pos=[pos.tag_ for e in graph.entities.values() for m in e.mentions.values() for num,pos in enumerate(nlp(sents[m.sentence_id])) if m.sentence_id in sents and num in m.indices]
		entities_pos=entities_pos+curr_entities_pos
	all_pos=len(entities_pos)
	noun_entities=len([pos for pos in entities_pos if pos in NOUNS])*1.00/all_pos
	adj_entities=len([pos for pos in entities_pos if pos in ADJECTIVES])*1.00/all_pos
	verb_entities=len([pos for pos in entities_pos if pos in VERBS])*1.00/all_pos
	other_entities=len([pos for pos in entities_pos if pos not in NOUNS+VERBS+ADJECTIVES])*1.00/all_pos
	print("nouns: "+str(noun_entities))
	print("adjectives: "+str(adj_entities))
	print("verbs: "+str(verb_entities))
	print("others: "+str(other_entities))

	#cheking average number of entities/propositions per argument:
	#step 1- group arguments across mentions
	args={p_num:set([(a.id,str(a.mention_type)+"_"+str(a.parent_id))  for m in p.mentions.values() for a_id,a in m.argument_mentions.iteritems()]) for graph in all_events for p_num,p in graph.propositions.iteritems() }
	#step 2- count disctinct elements in same arguments
	args_counted=[Counter([a[0] for a in elements]) for elements in args.values()]
	#step 3- average number of elements per arg:
	average_elements_argument=sum([number for counter in args_counted for number in counter.values()])*1.00/len([number for counter in args_counted for number in counter.values()])
	print("average_elements_per_arg: "+str(average_elements_argument))



	return 0

