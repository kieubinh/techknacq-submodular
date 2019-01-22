

import json
from lib.submodular.submodular import Submodular
from lib.submodular.constantvalues import ConstantValues
lambda_test=[0.0, 0.1, 0.3, 0.6, 1.0, 2.0]

def printResult(resultList):
    print("The number of selected list is "+str(len(resultList)))
    for doc in resultList:
        jsonDoc = json.loads(doc)
        print("id: "+jsonDoc['id']+" - title: "+jsonDoc['title'])
    
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
    #run with each lambda
    for Lambda in lambda_test:
        print("Lambda = "+str(Lambda))
        summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
        printResult(summarizedlist)

#run experiments for QFR method and UPR method
from lib.submodular.relevantdocuments import RelevantDocuments
def subQFR_UPR(path, query, method="qfr", type_sim="title"):

    #calculate similarity score between documents and query.
    relevantDocs = RelevantDocuments()
    relevantDocs.scroreTfIdfModel(path_raw=path)
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
    # run with each lambda
    for Lambda in lambda_test:
        print("Lambda = " + str(Lambda))
        summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
        printResult(summarizedlist)

#import os
#def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):

import click
@click.command()
@click.argument('concept_graph', type=click.Path(exists=True))
@click.argument('query', nargs=-1)
def main(concept_graph="concept-graph-standard.json", query="statistical parsing"):
    print(concept_graph)
    # subMMR_MCR(concept_graph, query, method="mcr", type_sim="text")
    subQFR_UPR(ConstantValues.SAMPLE, query, method="qfr", type_sim="text")

if __name__ == '__main__':

    main()