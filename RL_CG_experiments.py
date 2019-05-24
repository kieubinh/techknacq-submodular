import click

import RL_experiments as RLE
from lib.constantvalues import ConstantValues
from lib.elasticsearch.esexporter import ElasticsearchExporter
from lib.elasticsearch.essubmodular import ElasticsearchSubmodularity
from lib.submodular.articleinfo import ArticleInformation
from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList


def getlistID(year=10000, resultlist=None):
    # print(year)
    output = []

    for doc in resultlist:
        docid = doc['id']
        # print(doc)
        docyear = int(doc.get('year', '0'))
        # print(docyear)
        if docyear <= year:
            output.append(docid)

    return output

def recommendRLByCGMCR(index="acl2014", doc_type="json", concept_graph="concept-graph-standard.json", corpusInputPath="inputs/", resultPath="results/acl-cg-mcr/", method="mcr"):
    # load input
    inputDocs = RLE.loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = 1.0
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    for article in inputDocs:
        retrievedInfo = ArticleInformation(article)
        query = retrievedInfo.getQuery()
        # retrievedInfo.loadInforFromTitle(article)
        print(retrievedInfo.getId() + " : " + query)
        querylist = [query]
        rl = ReadingList(cg, querylist, learner_model)
        # get 10 relevant concepts for the query
        conceptlist = rl.getRelevantConcepts(max_matches=5)
        # add original query
        # conceptlist = {}
        conceptlist[query] = 1.0
        vDocs = ese.getRelevantDocsByCL(conceptlist, year=retrievedInfo.getYear(), max_each_matches=100)
        # print(vDocs)
        vlist = []
        for key in vDocs.keys():
            vlist.append(key)
        essub = ElasticsearchSubmodularity(esexport=ese, v=vlist, simq=vDocs, Lambda=Lambda)
        readinglist = essub.greedyAlgByCardinality(method=method)

        RLE.printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=essub.Lambda, resultPath=resultPath)


# input: query (in article)
# step 1: get relevant concepts from Gordon2016
# step 2: get similarity score between these concepts and each document
def recommendRLByCGMMR(index="acl2014", doc_type="json", concept_graph="concept-graph-standard.json", corpusInputPath="inputs/", resultPath="results/acl-cg-mmr/"):
    # load input
    inputDocs = RLE.loadInput(corpusInputPath)
    ese = ElasticsearchExporter(index=index, doc_type=doc_type)
    Lambda = 1.0
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    for article in inputDocs:
        retrievedInfo = ArticleInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        # print(article['info']['id'] + " : " + query)
        querylist = [retrievedInfo.getQuery()]
        r = ReadingList(cg, querylist, learner_model)
        # print reading list
        # r.print()

        # summarise the reading list

        # convert r into list of papers
        r.convert2List()
        rl = r.getReadinglist()
        vDocs = getlistID(year=retrievedInfo.getYear(), resultlist=rl)
        simq = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(), budget=1000)

        essub = ElasticsearchSubmodularity(esexport=ese, v=vDocs, simq=simq, Lambda=Lambda)
        readinglist = essub.greedyAlgByCardinality(method="qfr")

        RLE.printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=essub.Lambda, resultPath=resultPath)
        # RLE.printResult(articleId=retrievedInfo.getId(), output=rl, resultPath=resultPath)


def recommendRLByCGS(concept_graph="concept-graph-standard.json", corpusInputPath="sample-high/", resultPath="results/acl-top50/"):
    # load input
    inputDocs = RLE.loadInput(corpusInputPath)
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    for article in inputDocs:
        retrievedInfo = ArticleInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        # print(article['info']['id'] + " : " + query)
        querylist = [retrievedInfo.getQuery()]
        r = ReadingList(cg, querylist, learner_model)
        # print reading list
        # r.print()

        # summarise the reading list

        # convert r into list of papers
        r.convert2List()
        rl = r.getReadinglist
        RLE.print2File(article, rl, -1, resultPath=resultPath, budget=50000)


# ----------------------------- OLD VERSION -----------------------------------------------------------
# using tf-idf to get relevant documents, then using submodular function QFR to get subset of these -> very slow
def recommendRLByQfr(corpusPath, corpusInputPath, type_sim="text", resultPath=None):
    # load corpus
    relevantDocs = RLE.RelevantDocuments()
    relevantDocs.loadFromPath(corpusPath)

    # load input
    inputDocs = RLE.loadInput(corpusInputPath, resultPath)
    for article in inputDocs:

        retrievedInfo = ArticleInformation(article)
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
    inputDocs = loadInput(corpusInputPath, resultPath)
    for article in inputDocs:
        retrievedInfo = ArticleInformation(article)
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
        printResult(article_id="subQFR_UPR" + query, result=summarizedlist, Lambda=Lambda)


@click.command()
@click.argument('resultpath', type=click.Path())
@click.argument('parameters', nargs=-1)
def main(concept_graph="concept-graph-standard.json", resultpath="results/acl-cg/", parameters="cg qfr mmr mcr std", corpusInputPath="inputs/selection-6refs/"):
    print(resultpath)
    print(parameters)
    #mmr
    if "mmr" in parameters:
        recommendRLByCGMMR(concept_graph=concept_graph, corpusInputPath=corpusInputPath, resultPath=resultpath)
    if "mcr" in parameters:
        recommendRLByCGMCR(concept_graph=concept_graph, corpusInputPath=corpusInputPath, resultPath=resultpath, method="mcr")
    if "std" in parameters:
        recommendRLByCGS(concept_graph=concept_graph, corpusInputPath=corpusInputPath, resultPath=resultpath)

    if "qfr" in parameters:
        recommendRLByCGMCR(concept_graph=concept_graph, corpusInputPath=corpusInputPath, resultPath=resultpath, method="qfr")
    # # for concept graph
    # if "cg" in parameters:
    #     # default standard reading list from concept graph
    #     subMethod = "all"
    #
    #     if "mcr" in parameters:
    #         subMethod = "mcr"
    #     if "mmr" in parameters:
    #         subMethod = "mmr"
    #
    #     # default type sim = title
    #     type_sim = "title"
    #     if "abstract" in parameters:
    #         type_sim = "abstract"
    #     if "text" in parameters:
    #         type_sim = "text"
    #         # conceptgraph-19-01-19.json
    #     recommendRLByConceptGraph(concept_graph="conceptgraph-19-01-19.json", corpusInputPath=corpusInputPath,
    #                               resultPath=resultpath, subMethod=subMethod, type_sim=type_sim)


if __name__ == '__main__':
    main()
