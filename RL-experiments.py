#KieuBinh change
#au: author
#cg: concept graph
#top: tf-idf top 50
#es: elasticsearch
#mmr
#mcr
#qfres: query-focused relevance with elasticsearch

import click
import json

from lib.submodular.submodular import Submodular
from lib.constantvalues import ConstantValues
from lib.submodular.retrievedinfo import RetrievedInformation
# lambda_test=[0.0, 0.1, 0.3, 0.6, 1.0, 2.0]
lambda_test=[1.0]

#------------------------------- LOADING INPUT ----------------------------------------------
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

#------------------------------- RECOMMENDING READING LISTS METHODS ------------------------------------
from lib.elasticsearch.esexporter import ElasticsearchExporter
#Using ES to get relevant documents by authors,
# then using submodular function (QFR) to get subset of these
from lib.elasticsearch.essubmodular import ElasticsearchSubmodularity
def recommendRLByQfrAu(corpusPath, corpusInputPath, index="acl2014", doc_type="json"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    for article in inputDocs:
        refDocs = getReflistByAuthor(esexport=ese, article=article)
        print(len(refDocs))
        essub = ElasticsearchSubmodularity()



#Using ES to get CONSTANT.MAX_SUBMODULARITY relevant documents,
# then using submodular function (QFR) to get subset of these
def recommendRLByQfrEs(corpusPath, corpusInputPath, index="acl2014", doc_type="json"):
    return

def recommendRLByES(indexServer="acl2014", corpusInputPath="Jardine2014/", resultpath="results/es-top/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=indexServer)
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        query = retrievedInfo.getQuery()
        print(article['info']['id'] + " : " + query)
        year = int(article['info']['year'])
        resultlist = ese.queryByDSL(queryStr=query, year=year, budget=ConstantValues.BUDGET)
        output=[]
        for (key, value) in resultlist.items():
            output.append(key)
        printResult(articleId=article['info']['id'], output=output, resultPath=resultpath)

def getReflistByAuthor(esexport=None, article=None):
    if article==None:
        return []
    retrievedInfo = RetrievedInformation(article)
    # retrievedInfo.loadInforFromTitle(article)
    query = retrievedInfo.getQuery()
    year = retrievedInfo.getYear()
    authors = retrievedInfo.getAuthors()
    articleId = retrievedInfo.getId()
    print(articleId + " : " + query + " " + str(year) + " " + str(authors))
    refDocs = []
    for author in authors:
        auDocs = esexport.searchDocsByAuthor(author=author, year=year)
        for docId in auDocs:
            print(docId)
            if (docId != articleId):
                reflist = esexport.getReflist(id=docId)
                print(len(reflist))
                for refid in reflist:
                    if refid not in refDocs:
                        refDocs.append(refid)
    return refDocs

def recommendRLByAuthors(index="acl2014", corpusInputPath="inputs/", resultpath="results/acl-authors/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index)
    for article in inputDocs:
        refDocs = getReflistByAuthor(esexport=ese, article=article)
        print(len(refDocs))
        printResult(article['info']['id'], refDocs, -1, resultPath=resultpath)

#using tf-idf to get relevant documents, then using submodular function QFR to get subset of these -> very slow
def recommendRLByQfr(corpusPath, corpusInputPath,type_sim="text"):
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

#Using tf-idf to get top BUDGET relevant documents
def recommendRLByTop(corpusPath, corpusInputPath, resultPath):
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

#run experiments for MMR function and MCR function
from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList
def subMMR_MCR(concept_graph, query, method="mmr",type_sim = "title", article=None, resultPath="results/"):
    # print(concept_graph)
    # print(query)
    querylist = []
    querylist.append(query)
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    r = ReadingList(cg, querylist, learner_model)
    #print reading list
    # r.print()

    #summarise the reading list

    #convert r into list of papers
    r.convert2List()
    rl = r.getReadinglist()
    # print(rl)
    if len(rl)<=ConstantValues.BUDGET:
        #if length <= budget
        print2File(article, rl, -1, resultPath)
    else:
        #before summarization
        print("Before Submodular: ")
        # print(len(rl))
        # for doc in rl:
        #     print(doc['id']+" - "+str(doc))
        alg = ConstantValues.LAZY_GREEDY_ALG
        #Lambda = 0 -> no penalty
        submodular = Submodular()
        submodular.loadFromList(rl)
        #run with each lambda
        year = int(article['info'].get('year','10000'))
        for Lambda in lambda_test:
            print("Lambda = "+str(Lambda))
            summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim, year=year)
            print(len(summarizedlist))
            print2File(article, summarizedlist, Lambda, resultPath)

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
        printResult(articleId="subQFR_UPR"+query, output=summarizedlist, Lambda=Lambda)

#input: query (in article)
#output: reading list by Gordon 2017
def readinglistConceptGraph(concept_graph="conceptgraph-19-01-19.json", query="concept-to-text generation", article="acl-000-0000", resultPath="results/acl-cg-standard/"):
    querylist = []
    querylist.append(query)
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    r = ReadingList(cg, querylist, learner_model)
    # print reading list
    # r.print()

    # summarise the reading list

    # convert r into list of papers
    r.convert2List()
    rl = r.getReadinglist()
    print2File(article, rl, -1, resultPath, budget=50000)

def recommendRLByConceptGraph(concept_graph="concept-graph-standard.json", corpusInputPath="sample-high/", resultPath="results/acl-top50/", subMethod = "all", type_sim="title"):
    # load corpus
    # relevantDocs = RelevantDocuments()
    # relevantDocs.loadFromPath(corpusPath)

    # load input
    inputDocs = loadInput(corpusInputPath)
    for article in inputDocs:
        query = RetrievedInformation(article).getQuery()
        # retrievedInfo.loadInforFromTitle(article)
        print(article['info']['id'] + " : " + query)
        if subMethod == "all":
            readinglistConceptGraph(concept_graph=concept_graph, query=query, article=article, resultPath=resultPath)
        else:
            subMMR_MCR(concept_graph=concept_graph, query=query, method=subMethod, type_sim=type_sim, article=article, resultPath=resultPath)

#---------------------------------- PRINT RESULT -------------------------------------------
def print2File(article, resultList, Lambda, resultPath="", budget=ConstantValues.BUDGET):
    articleId = article['info']['id']
    year = int(article['info'].get('year','10000'))
    # print(year)
    output=[]
    count=0

    for doc in resultList:
        # print(doc['id'])
        if Lambda==-1:
            docid = doc['id']
            # print(doc)
            docyear = int(doc.get('year','0'))
        else:
            jsonDoc = json.loads(doc)
            docid=jsonDoc['info']['id']
            docyear = int(jsonDoc['info'].get('year','0'))

        # print(docyear)
        if docyear<=year:
            output.append(docid)
            count+=1
            # print(jsonDoc['query_score'])
            if count>=budget:
                break
    jsondoc = {
        'info': {
            'id': articleId,
            'count':count
        },
        'output': output,
    }
    print(resultPath+articleId+"-"+str(Lambda)+"-output.json")
    with open(resultPath+articleId+"-"+str(Lambda)+"-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()

def printResult(articleId, output, Lambda=-1, resultPath=""):
    print("number of output: "+str(len(output)))
    jsondoc = {
        'info': {
            'id': articleId,
            'count': len(output)
        },
        'output': output,
    }
    print(resultPath + articleId + "-" + str(Lambda) + "-output.json")
    with open(resultPath + articleId + "-" + str(Lambda) + "-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()

#---------------------------------- RUN EXPERIMENTS -------------------------------------------
#import os
#def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):

@click.command()
@click.argument('resultpath', type=click.Path())
@click.argument('parameters', nargs=-1)
#parameters:
#top: recommendRLByTop
#qfr: recommendRLByQfr
#cg: recommendRLByConceptGraph - standard, mmr, mcr (methods)
#es: using elasticsearch similarity score
def main(resultpath="results/acl-cg/", parameters="cg mmr title", corpusInputPath="inputs/"):
    print(parameters)
    print(resultpath)
    #authors
    if "au" in parameters:
        recommendRLByAuthors(indexServer="acl2014", corpusInputPath=corpusInputPath, resultpath=resultpath)
    if "es" in parameters:
        recommendRLByES(indexServer="acl2014", corpusInputPath=corpusInputPath, resultpath=resultpath)
    if "top" in parameters:
        recommendRLByTop(corpusPath="data/acl/", corpusInputPath=corpusInputPath, resultPath=resultpath)
    if "qfr" in parameters:
        recommendRLByQfr(corpusPath="data/acl-select/", corpusInputPath=corpusInputPath, type_sim="title")
    if "cg" in parameters:
        #default standard reading list from concept graph
        subMethod = "all"

        if "mcr" in parameters:
            subMethod="mcr"
        if "mmr" in parameters:
            subMethod="mmr"

        #default type sim = title
        type_sim = "title"
        if "abstract" in parameters:
            type_sim="abstract"
        if "text" in parameters:
            type_sim="text"
            #conceptgraph-19-01-19.json
        recommendRLByConceptGraph(concept_graph="conceptgraph-19-01-19.json", corpusInputPath=corpusInputPath,
                               resultPath=resultpath, subMethod = subMethod, type_sim=type_sim)
    #test case
    # subMMR_MCR(concept_graph, query, method="mmr", type_sim="title")
    # subQFR_UPR(path, query, method="qfr", type_sim="text", year=year)

if __name__ == '__main__':
    main()