

import json
from lib.submodular.submodular import Submodular
from lib.submodular.constantvalues import ConstantValues


#run experiments for MMR function and MCR function
from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList
def subMMR_MCR(concept_graph, query, method="mmr",type_sim = "title"):
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    r = ReadingList(cg, query, learner_model)
    #print reading list
    #r.print()

    #summarise the reading list

    #convert r into list of papers
    r.convert2List()
    rl = r.getReadinglist()
    #before summarization
    print("Before Submodular: ")
    print(len(rl))
    for doc in rl:
        print(doc['id']+" - "+str(doc))
    alg = ConstantValues.LAZY_GREEDY_ALG
    #Lambda = 0 -> no penalty
    submodular = Submodular()
    submodular.loadFromList(rl)
    print("Lambda = 0 -> No penalty")
    Lambda = 0.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])

    #Lambda = 0.5 -> less penalty
    print("Lambda = 0.1")
    Lambda = 0.1
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    #Lambda = 1.0 -> same degree penalty
    print("Lambda = 0.3")
    Lambda = 0.3
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    #Lambda = 2.0 -> double degree penalty
    print("Lambda = 0.6")
    Lambda = 0.6
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    #Lambda = 3.0 -> as paper
    print("Lambda = 1.0")
    Lambda = 1.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])

    # Lambda = 2.0 -> as paper
    print("Lambda = 2.0")
    Lambda = 2.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])


#run experiments for QFR method and UPR method
from lib.submodular.relevantdocuments import RelevantDocuments
def subQFR_UPR(path, query, method="qfr", type_sim="title"):

    #calculate similarity score between documents and query.
    relevantDocs = RelevantDocuments()
    #relevantDocs.loadFromPath(path)
    #generate tf idf model
    relevantDocs.trainTfIdfModel(path, "acl/")
    relevantDocs.loadFromTfIdfModel(path, "acl/")

    relevantDocs.findRankedTfIdf(query)

    # scores = relevantDocs.getTopResults(10, "tfidf")
    # print(scores)
    #
    # print(relevantDocs.getResultsByThreshold(0.01, "tfidf"))

    #run algorithm for submodular
    # before summarization
    print("Before Submodular: ")
    submodular = Submodular()
    submodular.loadFromCorpus(relevantDocs)
    alg = ConstantValues.LAZY_GREEDY_ALG
    print("Lambda = 0 -> No penalty")
    Lambda = 0.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])

    # Lambda = 0.5 -> less penalty
    print("Lambda = 0.1")
    Lambda = 0.1
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    # Lambda = 1.0 -> same degree penalty
    print("Lambda = 0.3")
    Lambda = 0.3
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    # Lambda = 2.0 -> double degree penalty
    print("Lambda = 0.6")
    Lambda = 0.6
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])
    # Lambda = 3.0 -> as paper
    print("Lambda = 1.0")
    Lambda = 1.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])

    # Lambda = 2.0 -> as paper
    print("Lambda = 2.0")
    Lambda = 2.0
    summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
    print(len(summarizedlist))
    for doc in summarizedlist:
        jsondoc = json.loads(doc)
        print(jsondoc['id'])


#import os
#def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):

import click
@click.command()
@click.argument('concept_graph', type=click.Path(exists=True))
@click.argument('query', nargs=-1)
def main(concept_graph="concept-graph-standard.json", query="statistical parsing"):
    print(concept_graph)
    # subMMR_MCR(concept_graph, query, method="mcr", type_sim="text")
    subQFR_UPR(ConstantValues.PATH, query, method="qfr", type_sim="text")

if __name__ == '__main__':

    main()