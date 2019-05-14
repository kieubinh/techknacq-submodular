# KieuBinh change
# au: author
# cg: concept graph
# top: tf-idf top 50
# es: elasticsearch
# mmr
# mcr
# qfres: query-focused relevance with elasticsearch

import click
import json

from lib.submodular.submodular import Submodular
from lib.constantvalues import ConstantValues
from lib.submodular.retrievedinfo import RetrievedInformation

# lambda_test=[0.0, 0.1, 0.3, 0.6, 1.0, 2.0]
# lambda_test = [1 - 1.0 * ConstantValues.BUDGET / ConstantValues.MAX_SUBMODULARITY]
lambda_test = [None]
# corpusInputPath = "inputs/selection-5refs/"
corpusInputPath = "inputs/selection-5refs/"
max_matches = 1
max_each_matches = 50
concept_graph = "concept-graphs/concept-graph-standard.json"
prefix_folder = "results/server/"
date_folder = "19-05-15/"
# prefix_sim = "acl-tfidf-sample-5refs-"
prefix_sim = "acl-tfidf-selection-5refs-"

# ------------------------------- LOADING INPUT ----------------------------------------------
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


# ------------------------------- RECOMMENDING READING LISTS METHODS ------------------------------------
from lib.elasticsearch.esexporter import ElasticsearchExporter
# Using ES to get relevant documents by authors,
# then using submodular function (QFR) to get subset of these
from lib.elasticsearch.essubmodular import ElasticsearchSubmodularity


def getVByQueryCG(ese=None, query=None, year=None, cg=None, learner_model=None):
    querylist = [query]
    # print(learner_model)
    rl = ReadingList(cg, querylist, learner_model)
    # get 10 relevant concepts for the query
    conceptlist = rl.getRelevantConcepts(max_matches)
    # do not account original query
    # if query not in conceptlist:
    #     conceptlist[query] = 1.0
    vDocs = ese.getRelevantDocsByCL(conceptlist=conceptlist, year=year, max_each_matches=max_each_matches)
    # print(vDocs)
    vlist = []
    for key in vDocs.keys():
        vlist.append(key)
    return vlist


def recommendRLByQfrAuEs(index="acl2014", doc_type="json", corpusInputPath=None, resultpath="results/acl-qfr-authors/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = lambda_test[0]
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        refDocs = getReflistByAuthors(esexport=ese, article=article)
        print(len(refDocs))
        simq = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                              budget=ConstantValues.MAX_SUBMODULARITY / 5)
        essub = ElasticsearchSubmodularity(esexport=ese, v=refDocs, simq=simq)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method="qfr")

        # essub = ElasticsearchSubmodularity(esexport=ese,query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),MAX_SIZE=1000)
        # readinglist = essub.greedyAlgByCardinality(v=refDocs,Lambda=Lambda, method="qfr")
        printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultpath)


def recommendRLByQfrAuCG(index="acl2014", doc_type="json", corpusInputPath=None, resultpath="results/acl-qfr-authors/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = lambda_test[0]
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    # print(learner_model)
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        # get articles by co-authors
        refDocs = getReflistByAuthors(esexport=ese, article=article)

        # get articles by query
        vlist = getVByQueryCG(ese=ese, query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                              learner_model=learner_model, cg=cg)
        num_au = len(refDocs)
        num_cg = len(vlist)
        # mix 2 lists
        for doc in refDocs:
            if doc not in vlist:
                vlist.append(doc)
        # calculate similarity score between query q and each article in v
        simq = ese.queryByURL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                              budget=ConstantValues.MAXSIZE)
        print("au: %i, cg: %i -> total: %i"%(num_au, num_cg, len(vlist)))
        essub = ElasticsearchSubmodularity(esexport=ese, v=vlist, simq=simq)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method="qfr")

        # essub = ElasticsearchSubmodularity(esexport=ese,query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),MAX_SIZE=1000)
        # readinglist = essub.greedyAlgByCardinality(v=refDocs,Lambda=Lambda, method="qfr")
        printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultpath)


# Using ES to get CONSTANT.MAX_SUBMODULARITY relevant documents,
# then using submodular function (QFR) to get subset of these
def recommendRLByQfrEs(index="acl2014", doc_type="json", corpusInputPath=None, resultpath="results/acl-qfr/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = lambda_test[0]
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        print(retrievedInfo.getId() + " " + retrievedInfo.getQuery() + " " + str(retrievedInfo.getYear()))
        # get 5000 relevant documents -> v = 5000
        vDocs = ese.queryByURL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                               budget=ConstantValues.MAX_SUBMODULARITY)

        # vDocs = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
        #                                                budget=ConstantValues.MAX_SUBMODULARITY)
        # print(len(vDocs))
        # qsim = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(), budget=5000)
        # print(vDocs)
        essub = ElasticsearchSubmodularity(esexport=ese, v=vDocs, simq=vDocs)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method="qfr")
        # essub = ElasticsearchSubmodularity(esexport=ese, query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
        #                                    MAX_SIZE=1000)
        # readinglist = essub.greedyAlgByCardinality(v=vDocs, Lambda=Lambda, method="qfr")
        printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultpath)


def recommendRLByQfrCG(index="acl2014", doc_type="json", corpusInputPath=None, resultpath="results/acl-qfr/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = lambda_test[0]
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        print(retrievedInfo.getId() + " " + retrievedInfo.getQuery() + " " + str(retrievedInfo.getYear()))
        # get 5000 relevant documents -> v = 5000
        vlist = getVByQueryCG(ese=ese, query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                              learner_model=learner_model, cg=cg)

        # vDocs = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
        #                                                budget=ConstantValues.MAX_SUBMODULARITY)
        # print(len(vDocs))
        simq = ese.queryByURL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
                              budget=ConstantValues.MAXSIZE)
        essub = ElasticsearchSubmodularity(esexport=ese, v=vlist, simq=simq)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method="qfr")

        printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultpath)


def recommendRLByES(index="acl2014", doc_type="json", corpusInputPath="Jardine2014/", resultpath="results/acl-top/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        query = retrievedInfo.getQuery()
        articleId = retrievedInfo.getId()
        year = retrievedInfo.getYear()
        print(articleId + " : " + query + " before " + str(year))
        resultlist = ese.queryByURL(query=query, year=year+1, budget=ConstantValues.BUDGET)
        output = []
        for (key, value) in resultlist.items():
            output.append(key)
        printResult(articleId=articleId, output=output, resultPath=resultpath)


def getReflistByAuthors(esexport=None, article=None):
    if article is None:
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
            # print(docId)
            if docId != articleId:
                reflist = esexport.getReflist(id=docId)
                # print(len(reflist))
                for refid in reflist:
                    if refid not in refDocs:
                        refDocs.append(refid)
    return refDocs


def recommendRLByAuthors(index="acl2014", doc_type="json", corpusInputPath="inputs/", resultpath="results/acl-au/"):
    inputDocs = loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    for article in inputDocs:
        refDocs = getReflistByAuthors(esexport=ese, article=article)
        print(len(refDocs))
        printResult(article['info']['id'], refDocs, -1, resultPath=resultpath)


# using tf-idf to get relevant documents, then using submodular function QFR to get subset of these -> very slow
def recommendRLByQfr(corpusPath, corpusInputPath, type_sim="text"):
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

        # get all for baseline
        # print2File(article, submodular.getDocs(), 100)

        # use submodular to select
        alg = ConstantValues.LAZY_GREEDY_ALG
        # run with each lambda
        for Lambda in lambda_test:
            print("Lambda = " + str(Lambda))
            summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method="qfr", type_sim=type_sim)
            print2File(article, summarizedlist, Lambda)


# Using tf-idf to get top BUDGET relevant documents
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


# run experiments for MMR function and MCR function
from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList


def subMMR_MCR(concept_graph, query, method="mmr", type_sim="title", article=None, resultPath="results/"):
    # print(concept_graph)
    # print(query)
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
    rl = r.getReadinglist
    # print(rl)
    if len(rl) <= ConstantValues.BUDGET:
        # if length <= budget
        print2File(article, rl, -1, resultPath)
    else:
        # before summarization
        print("Before Submodular: ")
        # print(len(rl))
        # for doc in rl:
        #     print(doc['id']+" - "+str(doc))
        alg = ConstantValues.LAZY_GREEDY_ALG
        # Lambda = 0 -> no penalty
        submodular = Submodular()
        submodular.loadFromList(rl)
        # run with each lambda
        year = int(article['info'].get('year', '10000'))
        for Lambda in lambda_test:
            print("Lambda = " + str(Lambda))
            summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim, year=year)
            print(len(summarizedlist))
            print2File(article, summarizedlist, Lambda, resultPath)


# run experiments for QFR method and UPR method
from lib.submodular.relevantdocuments import RelevantDocuments


def subQFR_UPR(path, query, method="qfr", type_sim="title", year=10000):
    # calculate similarity score between documents and query.
    relevantDocs = RelevantDocuments()
    # relevantDocs.scroreTfIdfModel(path_raw=path)
    relevantDocs.loadFromPath(path, year)
    # generate tf idf model
    # relevantDocs.trainTfIdfModel(path, "acl/")
    # relevantDocs.loadFromTfIdfModel(path, "acl/")

    relevantDocs.findRankedTfIdf(query)

    # scores = relevantDocs.getTopResults(10, "tfidf")
    # print(scores)
    #
    # print(relevantDocs.getResultsByThreshold(0.01, "tfidf"))

    # run algorithm for submodular
    # before summarization
    print("Before Submodular: ")
    submodular = Submodular()
    submodular.loadFromCorpus(relevantDocs)
    alg = ConstantValues.LAZY_GREEDY_ALG
    # run with each lambda
    for Lambda in lambda_test:
        print("Lambda = " + str(Lambda))
        summarizedlist = submodular.getSubmodular(alg, Lambda=Lambda, method=method, type_sim=type_sim)
        printResult(articleId="subQFR_UPR" + query, output=summarizedlist, Lambda=Lambda)


# ---------------------------------- PRINT RESULT -------------------------------------------
def print2File(article, resultList, Lambda, resultPath="", budget=ConstantValues.BUDGET):
    articleId = article['info']['id']
    year = int(article['info'].get('year', '10000'))
    # print(year)
    output = []
    count = 0

    for doc in resultList:
        # print(doc['id'])
        if Lambda == -1:
            docid = doc['id']
            # print(doc)
            docyear = int(doc.get('year', '0'))
        else:
            jsonDoc = json.loads(doc)
            docid = jsonDoc['info']['id']
            docyear = int(jsonDoc['info'].get('year', '0'))

        # print(docyear)
        if docyear <= year:
            output.append(docid)
            count += 1
            # print(jsonDoc['query_score'])
            if count >= budget:
                break
    jsondoc = {
        'info': {
            'id': articleId,
            'count': count
        },
        'output': output,
    }
    print(resultPath + articleId + "-" + str(Lambda) + "-output.json")
    with open(resultPath + articleId + "-" + str(Lambda) + "-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()


def printResult(articleId, output, Lambda=-1.0, resultPath=""):
    print("number of output: " + str(len(output)))
    # print(output)
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


# ---------------------------------- RUN EXPERIMENTS -------------------------------------------
# import os
# def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):

@click.command()
# @click.argument('resultpath', type=click.Path())
@click.argument('parameters', nargs=-1)
# parameters:
# top: recommendRLByTop
# qfr: recommendRLByQfr
# cg: recommendRLByConceptGraph - standard, mmr, mcr (methods)
# es: using elasticsearch similarity score
# corpusInputPath="inputs/survey/selected/"
# corpusInputPath="inputs/100-random/"
def main(resultpath=None, parameters="es au qfr cg"):
    print(parameters)
    index = ConstantValues.ACL_CORPUS_INDEX
    doctype = ConstantValues.ACL_CORPUS_DOCTYPE

    # es -> au / not au
    # au -> qfr / all
    # for es
    if resultpath is None:
        resultpath = prefix_folder + date_folder + prefix_sim + parameters[0] \
                     + "-" + str(ConstantValues.Alpha) + "-" + str(ConstantValues.Lambda) \
                     + "-" + str(max_matches) + "-" + str(max_each_matches) + "/"

    print(resultpath)
    if not os.path.exists(resultpath):
        os.makedirs(resultpath)

    if "es-au-qfr-cg" in parameters:
        recommendRLByQfrAuCG(index=index, doc_type=doctype, corpusInputPath=corpusInputPath,
                             resultpath=resultpath)
    if "es-au-qfr" in parameters:
        recommendRLByQfrAuEs(index=index, doc_type=doctype, corpusInputPath=corpusInputPath,
                             resultpath=resultpath)
    if "es-au" in parameters:
        recommendRLByAuthors(index=index, doc_type=doctype, corpusInputPath=corpusInputPath,
                             resultpath=resultpath)
    if "es-qfr-cg" in parameters:
        recommendRLByQfrCG(index=index, doc_type=doctype, corpusInputPath=corpusInputPath,
                           resultpath=resultpath)

    if "es-qfr" in parameters:
        recommendRLByQfrEs(index=index, doc_type=doctype, corpusInputPath=corpusInputPath, resultpath=resultpath)

    if "es" in parameters:
        # only es - get top budget
        recommendRLByES(index=index, doc_type=doctype, corpusInputPath=corpusInputPath, resultpath=resultpath)

    # for tf-idf
    if "es" not in parameters:
        if "top" in parameters:
            recommendRLByTop(corpusPath="data/acl/", corpusInputPath=corpusInputPath, resultPath=resultpath)
        if "qfr" in parameters:
            recommendRLByQfr(corpusPath="data/acl-select/", corpusInputPath=corpusInputPath, type_sim="title")

            # test case
            # subMMR_MCR(concept_graph, query, method="mmr", type_sim="title")
            # subQFR_UPR(path, query, method="qfr", type_sim="text", year=year)


if __name__ == '__main__':
    main()
