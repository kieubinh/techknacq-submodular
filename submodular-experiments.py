
import click
import json
from lib.submodular.submodular import Submodular
from lib.submodular.constantvalues import ConstantValues
from lib.submodular.retrievedinfo import RetrievedInformation
# lambda_test=[0.0, 0.1, 0.3, 0.6, 1.0, 2.0]
lambda_test=[2.0]

def print2File(article, resultList, Lambda, resultPath=""):
    articleId = article['info']['id']
    output=[]
    count=0
    for doc in resultList:
        jsonDoc = json.loads(doc)
        output.append(jsonDoc['info']['id'])
        count+=1
        # print(jsonDoc['query_score'])
        if count>ConstantValues.BUDGET:
            break
    jsondoc = {
        'info': {
            'id': articleId
        },
        'output': output,
    }
    with open(resultPath+articleId+"-"+str(Lambda)+"-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()

def printResult(resultList):
    print("The number of selected list is "+str(len(resultList)))
    for doc in resultList:
        jsonDoc = json.loads(doc)
        print("id: "+jsonDoc['info']['id']+" - title: "+jsonDoc['info']['title'])
    
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
def subQFR_UPR(path, query, method="qfr", type_sim="title", year=10000):

    #calculate similarity score between documents and query.
    relevantDocs = RelevantDocuments()
    # relevantDocs.scroreTfIdfModel(path_raw=path)
    relevantDocs.loadFromPath(path, year)
    #generate tf idf model
    # relevantDocs.trainTfIdfModel(path, "acl/")
    # relevantDocs.loadFromTfIdfModel(path, "acl/")

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

import os
import io
import sys

def loadInput(corpusInputPath="sample-high/"):
    corpusInput = []
    for root, dirs, files in os.walk(corpusInputPath, topdown=False):
        for nameFile in files:
            if "json" in nameFile:
                try:
                    data = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                    corpusInput.append(data)
                    # print(nameId)

                except Exception as e:
                    print('Error reading JSON document:', nameFile, file=sys.stderr)
                    print(e, file=sys.stderr)
                    sys.exit(1)
    return corpusInput

def recommendRefByQfr(corpusPath, corpusInputPath,type_sim="text"):
    #load corpus
    relevantDocs = RelevantDocuments()
    relevantDocs.loadFromPath(corpusPath)

    #load input
    inputDocs = loadInput(corpusInputPath)
    for article in inputDocs:

        retrievedInfo = RetrievedInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        query = retrievedInfo.getQuery()
        print(article['info']['id']+" : "+query)
        year = int(article['info']['year'])

        relevantDocs.findRankedTfIdf(query)

        # scores = relevantDocs.getTopResults(10, "tfidf")
        # print(scores)
        #
        # print(relevantDocs.getResultsByThreshold(0.01, "tfidf"))

        # run algorithm for submodular
        # before summarization
        print("Before Submodular: ")
        submodular = Submodular()
        submodular.loadFromCorpusByYear(relevantDocs, year)

        #get all for baseline
        # print2File(article, submodular.getDocs(), 100)

        #use submodular to select
        alg = ConstantValues.LAZY_GREEDY_ALG
        # run with each lambda
        for Lambda in lambda_test:
            print("Lambda = " + str(Lambda))
            summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method="qfr", type_sim=type_sim)
            print2File(article, summarizedlist, Lambda)

def recommendRefByTop(corpusPath, corpusInputPath, resultPath):
    # load corpus
    relevantDocs = RelevantDocuments()
    relevantDocs.loadFromPath(corpusPath)

    # load input
    inputDocs = loadInput(corpusInputPath)
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        query = retrievedInfo.getQuery()
        print(article['info']['id'] + " : " + query)
        year = int(article['info']['year'])

        relevantDocs.findRankedTfIdf(query)

        # scores = relevantDocs.getTopResults(10, "tfidf")
        # print(scores)
        #
        # print(relevantDocs.getResultsByThreshold(0.01, "tfidf"))

        # run algorithm for submodular
        # before summarization
        print("Before Submodular: ")
        submodular = Submodular()
        submodular.loadFromCorpusByYear(relevantDocs, year)

        # get relevant top for baseline
        print2File(article, submodular.getDocs(), ConstantValues.BUDGET, resultPath)

#import os
#def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):


# @click.command()
# @click.argument('path', type=click.Path(exists=True))
# @click.argument('query', nargs=-1)
def main(path="data/acl-score-select/", query="Towards Robust Linguistic Analysis Using OntoNotes", year=2013):
    print(path)
    # subMMR_MCR(concept_graph, query, method="mmr", type_sim="title")
    subQFR_UPR(path, query, method="qfr", type_sim="text", year=year)

if __name__ == '__main__':
    # recommendRefByQfr(corpusPath="data/acl-select/", corpusInputPath="sample-high/", type_sim="title")
    recommendRefByTop(corpusPath="data/acl/", corpusInputPath="sample-high/", resultPath="results/acl-top50/")
    # main()