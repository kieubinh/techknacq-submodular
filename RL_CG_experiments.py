import click

from lib.submodular.retrievedinfo import RetrievedInformation
from lib.techknacq.readinglist import ReadingList
from lib.techknacq.conceptgraph import ConceptGraph
from lib.constantvalues import ConstantValues
from lib.elasticsearch.essubmodular import ElasticsearchSubmodularity
from lib.elasticsearch.esexporter import ElasticsearchExporter

import RL_experiments as RLE


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
        retrievedInfo = RetrievedInformation(article)
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
        essub = ElasticsearchSubmodularity(esexport=ese, v=vlist, qsim=vDocs)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method=method)

        RLE.printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultPath)


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
        retrievedInfo = RetrievedInformation(article)
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
        qsim = ese.queryByDSL(query=retrievedInfo.getQuery(), year=retrievedInfo.getYear(), budget=1000)

        essub = ElasticsearchSubmodularity(esexport=ese, v=vDocs, qsim=qsim)
        readinglist = essub.greedyAlgByCardinality(Lambda=Lambda, method="qfr")

        RLE.printResult(articleId=retrievedInfo.getId(), output=readinglist, Lambda=Lambda, resultPath=resultPath)
        # RLE.printResult(articleId=retrievedInfo.getId(), output=rl, resultPath=resultPath)


def recommendRLByCGS(concept_graph="concept-graph-standard.json", corpusInputPath="sample-high/", resultPath="results/acl-top50/"):
    # load input
    inputDocs = RLE.loadInput(corpusInputPath)
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    for article in inputDocs:
        retrievedInfo = RetrievedInformation(article)
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


@click.command()
@click.argument('resultpath', type=click.Path())
@click.argument('parameters', nargs=-1)
def main(concept_graph="concept-graph-standard.json", resultpath="results/acl-cg/", parameters="cg qfr mmr mcr std", corpusInputPath="inputs/"):
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
