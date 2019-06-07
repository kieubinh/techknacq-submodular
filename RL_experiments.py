# KieuBinh change
# au: author
# cg: concept graph
# top: tf-idf top 50
# es: elasticsearch
# mmr
# mcrp
# qfres: query-focused relevance with elasticsearch

import click
import json
import os
import io

from lib.constantvalues import ConstantValues
from lib.submodular.articleinfo import ArticleInformation
from lib.elasticsearch.esexporter import ElasticsearchExporter
from lib.elasticsearch.essubmodular import ElasticsearchSubmodularity
from lib.utils import Utils

from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList

# lambda_test=[0.0, 0.1, 0.3, 0.6, 1.0, 2.0]
# lambda_test = [1 - 1.0 * ConstantValues.BUDGET / ConstantValues.MAX_SUBMODULARITY]
lambda_test = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# lambda_test = [-1]
# lambda_test = [0.0, 0.1, 0.2, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# corpusInputPath = "inputs/selection-5refs/"
# corpusInputPath = "inputs/sample-12-1/"
corpusInputPath = "inputs/selection-12-1/"
# corpusInputPath = "inputs/survey/selected/"
concept_graph = "concept-graphs/concept-graph-standard.json"
prefix_folder = "results/server/"
date_folder = "19-06-07/"
# prefix_sim = "acl-tfidf-sample-5refs-"
# prefix_sim = "acl-bm25-sample-12-1-"
prefix_sim = "acl-bm25-selection-12-1-"
# prefix_sim = "acl-bm25-selection-5refs-"
# prefix_sim = "acl-bm25-survey-"
# elasticsearch

# conti = True -> run continue: ignore exist files
conti = True
# 1.0 for submodular algorithm, -1 for others
lambda_check=1.0
# v2 for average, v1 for max
# default_sub_method = ConstantValues.Maximal_Marginal_Relevance_v3
default_sub_method = ConstantValues.Query_Author_Influence_v2
# concept graph
max_matches = 1
max_each_matches = 1
default_resultPath = prefix_folder + date_folder + prefix_sim + default_sub_method\
                     + "-" + str(ConstantValues.BUDGET) + "-" + str(max_matches) + "-" + str(max_each_matches) + "/"


# 1.0 - 1.0 * ConstantValues.BUDGET / max(len(v), 1)
# ------------------------------- LOADING INPUT ----------------------------------------------
def getResultQuery(article_info=None, budget=ConstantValues.BUDGET):
    # using query MLT = entire manuscript
    return getMltFromFile(article_id=article_info.getId(), year=article_info.getYear(), budget=budget)
    # using query = title + abstract
    # return ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(), budget=budget)


def get_author_score(ese=None, article_info=None):
    # return: score between doc i with article based on author relations
    # + 2 for each paper with same authors
    # + 1 for references of paper with same authors
    # 0 for others
    authors_score = {}
    authors = article_info.getAuthors()
    for author in authors:
        docs_by_author = ese.searchDocsByAuthor(author=author, year=article_info.getYear())
        for doc_id in docs_by_author:
            # add 2 for each doc
            if doc_id not in authors_score:
                authors_score[doc_id] = ConstantValues.SCORE_SAME_AUTHORS
            else:
                authors_score[doc_id] += ConstantValues.SCORE_SAME_AUTHORS
            # get references to add 1
            ref_list = ese.getReflist(id=doc_id)
            # print(len(reflist))
            for ref_id in ref_list:
                if ref_id not in authors_score:
                    authors_score[ref_id] = ConstantValues.SCORE_REF_SAME_AUTHORS
                else:
                    authors_score[ref_id] += ConstantValues.SCORE_REF_SAME_AUTHORS

    return authors_score


def loadInput(corpusInputPath="sample-high/", resultPath=None):
    if resultPath is None:
        resultPath = default_resultPath
    expPath = genExpPath(resultPath, Lambda=lambda_check)
    # load result path
    exist_ids = []
    # if run continue
    if conti is True:
        if expPath is not None:
            for root, dirs, files in os.walk(expPath, topdown=False):
                for nameFile in files:
                    try:
                        data = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                        exist_ids.append(data['info']['id'])
                        # print(nameId)

                    except Exception as e:
                        print('Error reading JSON document:', nameFile)

    # load corpus path
    corpusInput = []
    for root, dirs, files in os.walk(corpusInputPath, topdown=False):
        for nameFile in files:
            if "json" in nameFile:
                try:
                    data = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                    if data['info']['id'] not in exist_ids:
                        corpusInput.append(data)
                        # print(nameId)

                except Exception as e:
                    print('Error reading JSON document:', nameFile)
                    # sys.exit(1)
    return corpusInput


def genExpPath(resultPath=default_resultPath, Lambda=1.0):
    return resultPath + str(Lambda) + "/"


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


def getReflistByAuthors(ese=None, article_info=None):
    if article_info is None:
        return []

    # retrievedInfo.loadInforFromTitle(article)
    query = article_info.getQuery()
    year = article_info.getYear()
    authors = article_info.getAuthors()
    articleId = article_info.getId()
    print(articleId + " : " + query + " " + str(year) + " " + str(authors))
    refDocs = []
    for author in authors:
        auDocs = ese.searchDocsByAuthor(author=author, year=year)
        for docId in auDocs:
            # print(docId)
            if docId != articleId:
                reflist = ese.getReflist(id=docId)
                # print(len(reflist))
                for refid in reflist:
                    if refid not in refDocs:
                        refDocs.append(refid)
    return refDocs

# ------------------------------- RECOMMENDING READING LISTS METHODS ------------------------------------
# Using ES to get relevant documents by authors,
# then using submodular function (QFR) to get subset of these
def retrievedModel(method="mlt", resultPath=default_resultPath):
    inputDocs = loadInput(corpusInputPath, resultPath)
    missing_articles = []
    print("Number of document inputs: %i" % len(inputDocs))
    for article in inputDocs:
        article_info = ArticleInformation(article)
        # retrievedInfo.loadInforFromTitle(article)
        query = article_info.getQuery()
        article_id = article_info.getId()
        year = article_info.getYear()
        if year == 0:
            # ignore doc with no abstract
            missing_articles.append(article_id)
            continue
        print(article_id + " : " + query + " before " + str(year))

        directMethod(article_info=article_info, method=method)

    print("missing articles: ")
    print(missing_articles)


def directMethod(article_info=None, method="mlt", resultPath=default_resultPath):
    # baseline methods not use ES
    if method == ConstantValues.More_Like_This:
        recommendRLByMlt(article_id=article_info.getId(), year=article_info.getYear(), resultPath=resultPath)
        return

    # for methods needed ES
    ese = ElasticsearchExporter(index=ConstantValues.ACL_CORPUS_INDEX, doc_type=ConstantValues.ACL_CORPUS_DOCTYPE)
    if method == ConstantValues.ES:
        recommendRLByEs(ese=ese, article_info=article_info, resultPath=resultPath)
        return

    if method == ConstantValues.ES_SUB:
        recommendRLByEsSub(ese=ese, article_info=article_info, resultPath=resultPath)
        return

    if method == ConstantValues.ES_AU:
        recommendRLByEsAu(ese=ese, article_info=article_info, resultPath=resultPath)
        return

    if method == ConstantValues.ES_AU_SUB:
        recommendRLByEsAuSub(ese=ese, article_info=article_info, resultPath=resultPath)
        return
    if method == ConstantValues.ES_AU_SUB_CG:
        recommendRLByEsAuSubCg(ese=ese, article_info=article_info, resultPath=resultPath)
        return
    if method == ConstantValues.ES_AU_SUB_TOP:
        recommendRLByEsAuSubTop(ese=ese, article_info=article_info, resultPath=resultPath)
        return

    if method == ConstantValues.ES_SUB_CG:
        recommendRLByEsSubCg(ese=ese, article_info=article_info, resultPath=resultPath)
        return


def getMltFromFile(article_id=None, year=0, budget=ConstantValues.BUDGET):
    print(article_id, year, budget)
    sim_docs = Utils.getSimDocFromCorpus(article_id)
    recency_sim_docs = {}
    for doc_id, score in sim_docs.items():
        doc_year = Utils.getYearFromId(doc_id)
        if doc_year < year:
            recency_sim_docs[doc_id] = score + (doc_year - year) * ConstantValues.w_years

    sorted_recency_sim_docs = sorted(recency_sim_docs.items(), key=lambda x: x[1], reverse=True)
    count = 0
    result = {}
    for doc_id, score in sorted_recency_sim_docs:
        result[doc_id] = score
        count += 1
        if count >= budget:
            return result
    return result


def recommendRLByMlt(article_id=None, year=None, resultPath=default_resultPath):
    result = getMltFromFile(article_id=article_id, year=year)
    # print(output)
    # output=[]
    # for (key, value) in resultlist.items():
    #     output.append(key)
    printResult(article_id=article_id, result=result, resultPath=resultPath)


def recommendRLByEs(ese=None, article_info=None, resultPath=default_resultPath):
    retrieved_list = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
                                    budget=ConstantValues.BUDGET)
    printResult(article_id=article_info.getId(), result=retrieved_list, resultPath=resultPath)


# Using ES to get CONSTANT.MAX_SUBMODULARITY relevant documents,
# then using submodular function (SUB) to get subset of these
def recommendRLByEsSub(ese=None, article_info=None, resultPath=default_resultPath):
    vDocs = getResultQuery(article_info=article_info, budget=ConstantValues.MAX_SUBMODULARITY)
    if vDocs is None:
        # ignore error timeout or no answer
        return {}
    essub = ElasticsearchSubmodularity(ese=ese, v=vDocs, simq=vDocs)

    for Lambda in lambda_test:
        retrieved_list = essub.greedyAlgByCardinality(method=default_sub_method, Lambda=Lambda)
        # essub = ElasticsearchSubmodularity(esexport=ese, query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),
        #                                    MAX_SIZE=1000)
        # readinglist = essub.greedyAlgByCardinality(v=vDocs, Lambda=Lambda, method="SUB")
        printResult(article_id=article_info.getId(), result=retrieved_list, Lambda=Lambda, resultPath=resultPath)


def recommendRLByEsAu(ese=None, article_info=None, resultPath=default_resultPath):
    retrieved_list = getReflistByAuthors(ese=ese, article_info=article_info)
    print(len(retrieved_list))
    printResult(article_id=article_info.getId(), result=retrieved_list, resultPath=resultPath)

import collections

def recommendRLByEsAuSub(ese=None, article_info=None, resultPath=default_resultPath):
    vDocs = getResultQuery(article_info=article_info, budget=ConstantValues.MAX_SUBMODULARITY)

    if vDocs is None:
        # ignore error timeout or no answer
        return {}

    # Get top 100 relevant query similarity scores, Lambda = -1
    output = Utils.get_top_dict(dict=vDocs, budget=ConstantValues.BUDGET)

    printResult(article_id=article_info.getId(), result=output, Lambda=-1, resultPath=resultPath)

    # simq = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
    #                       budget=ConstantValues.MAXSIZE)
    # simq = getResultQuery(article_info=article_info, budget=ConstantValues.MAXSIZE)
    authors_score = get_author_score(ese=ese, article_info=article_info)
    print(authors_score)
    # Get top 100 authors_score, Lambda = -2
    output = Utils.get_top_dict(dict=authors_score, budget=ConstantValues.BUDGET)
    printResult(article_id=article_info.getId(), result=output, Lambda=-2, resultPath=resultPath)

    essub = ElasticsearchSubmodularity(ese=ese, v=vDocs, simq=vDocs,
                                       authors_score=authors_score, year=article_info.getYear())
    # Get top 100 influence scores, Lambda = -3
    inf_docs = {}
    for doc_id, cite_docs in essub.cite_to.items():
        inf_docs[doc_id] = len(cite_docs)
    output = Utils.get_top_dict(dict=inf_docs, budget=ConstantValues.BUDGET)
    printResult(article_id=article_info.getId(), result=output, Lambda=-3, resultPath=resultPath)

    for Lambda in lambda_test:
        retrieved_list = essub.greedyAlgByCardinality(method=default_sub_method, Lambda=Lambda)
        printResult(article_id=article_info.getId(), result=retrieved_list, Lambda=Lambda, resultPath=resultPath)


def recommendRLByEsAuSubCg(ese=None, article_info=None, resultPath=default_resultPath):
    # from authors
    refDocs = getReflistByAuthors(ese=ese, article_info=article_info)

    # from CG
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    # print(learner_model)

    # get articles by query
    vlist = getVByQueryCG(ese=ese, query=article_info.getQuery(), year=article_info.getYear(),
                          learner_model=learner_model, cg=cg)
    num_au = len(refDocs)
    num_cg = len(vlist)
    # mix 2 lists
    for doc in refDocs:
        if doc not in vlist:
            vlist.append(doc)
    # calculate similarity score between query q and each article in v
    # simq = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
    #                       budget=ConstantValues.MAXSIZE)
    simq = getResultQuery(article_info=article_info, budget=ConstantValues.MAXSIZE)
    print("au: %i, cg: %i -> total: %i" % (num_au, num_cg, len(vlist)))
    essub = ElasticsearchSubmodularity(ese=ese, v=vlist, simq=simq)
    for Lambda in lambda_test:
        readinglist = essub.greedyAlgByCardinality(method=default_sub_method, Lambda=Lambda)

        # essub = ElasticsearchSubmodularity(esexport=ese,query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(),MAX_SIZE=1000)
        # readinglist = essub.greedyAlgByCardinality(v=refDocs,Lambda=Lambda, method="SUB")
        printResult(article_id=article_info.getId(), result=readinglist, Lambda=Lambda, resultPath=resultPath)


def recommendRLByEsAuSubTop(ese=None, article_info=None, resultPath="results/acl-SUB-au-top/"):
    # get articles by co-authors
    refDocs = getReflistByAuthors(ese=ese, article_info=article_info)
    # get articles by query
    # topDocs = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
    #                          budget=max_each_matches)
    # calculate similarity score between query q and each article in v
    # simq = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
    #                       budget=ConstantValues.MAXSIZE)
    simq = getResultQuery(article_info=article_info, budget=ConstantValues.MAXSIZE)
    # get top 100
    topDocs = simq[:max_each_matches]

    vlist = []
    if refDocs is None:
        num_au = 0
    else:
        num_au = len(refDocs)
        # mix 2 lists
        for doc in refDocs:
            if doc not in vlist:
                vlist.append(doc)
    if topDocs is None:
        num_top = 0
    else:
        num_top = len(topDocs)
        for doc in topDocs:
            if doc not in vlist:
                vlist.append(doc)

    print("au: %i, top: %i -> total: %i" % (num_au, num_top, len(vlist)))
    essub = ElasticsearchSubmodularity(ese=ese, v=vlist, simq=simq)

    for Lambda in lambda_test:
        readinglist = essub.greedyAlgByCardinality(method=default_sub_method, Lambda=Lambda)
        printResult(article_id=article_info.getId(), result=readinglist, Lambda=Lambda, resultPath=resultPath)


def recommendRLByEsSubCg(ese=None, article_info=None, resultPath=default_resultPath):
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER

    # get 5000 relevant documents -> v = 5000
    vlist = getVByQueryCG(ese=ese, query=article_info.getQuery(), year=article_info.getYear(),
                          learner_model=learner_model, cg=cg)

    # simq = ese.queryByURL(query=article_info.getQuery(), year=article_info.getYear(),
    #                       budget=ConstantValues.MAXSIZE)
    simq = getResultQuery(article_info=article_info, budget=ConstantValues.MAXSIZE)
    essub = ElasticsearchSubmodularity(ese=ese, v=vlist, simq=simq)
    for Lambda in lambda_test:
        readinglist = essub.greedyAlgByCardinality(method=default_sub_method, Lambda=Lambda)
        printResult(article_id=article_info.getId(), result=readinglist, Lambda=Lambda, resultPath=resultPath)


# ---------------------------------- PRINT RESULT -------------------------------------------
def print2File(article, resultList, Lambda=-1, resultPath=default_resultPath, budget=ConstantValues.BUDGET):
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
    exp_path = genExpPath(resultPath=resultPath, Lambda=Lambda)
    if not os.path.exists(exp_path):
        os.makedirs(exp_path)
    print(exp_path + articleId + "-output.json")
    with open(exp_path + articleId + "-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()


def printResult(article_id=None, result=None, Lambda=-1.0, resultPath=default_resultPath):
    if article_id is None:
        print("No information about article to print!", result)
        return
    output = []
    if result is not None:
        for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True):
            output.append(k)
    print("number of output: " + str(len(output)))
    # print(output)
    jsondoc = {
        'info': {
            'id': article_id,
            'count': len(output)
        },
        'output': output,
    }
    exp_path = genExpPath(resultPath=resultPath, Lambda=Lambda)
    if not os.path.exists(exp_path):
        os.makedirs(exp_path)
    print(exp_path + article_id + "-output.json")
    with open(exp_path + article_id + "-output.json", 'w', encoding='utf-8') as fout:
        json.dump(jsondoc, fout)
    fout.close()


# ---------------------------------- RUN EXPERIMENTS -------------------------------------------
# import os
# def main(concept_graph=os.getcwd()+"/concept-graph-standard.json", query="statistical parsing"):

@click.command()
# @click.argument('resultPath', type=click.Path())
@click.argument('methods', nargs=-1)
# parameters:
# top: recommendRLByTop
# sub: recommendRLBySub
# cg: recommendRLByConceptGraph - standard, mmr, mcr (methods)
# es: using elasticsearch similarity score
# corpusInputPath="inputs/survey/selected/"
# corpusInputPath="inputs/100-random/"
def main(methods="es au sub cg continue"):
    print(methods)

    # es -> au / not au
    # au -> sub / all
    # for es
    resultPath = default_resultPath

    for method in methods:
        print(method)
        retrievedModel(method=method, resultPath=resultPath)

        # test case
        # subMMR_MCR(concept_graph, query, method="mmr", type_sim="title")
        # subQFR_UPR(path, query, method="qfr", type_sim="text", year=year)


if __name__ == '__main__':
    main()
