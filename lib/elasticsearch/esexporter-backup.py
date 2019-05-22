import io
import json
import sys
from pathlib import Path
import multiprocessing as mp

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from lib.constantvalues import ConstantValues
from lib.submodular.articleinfo import RetrievedInformation
from lib.document.simscores import SimilairtyScores


# from elasticsearch_dsl.query import MultiMatch, Match
# from elasticsearch_dsl.query import MoreLikeThis


class ElasticsearchExporter:
    def __init__(self, index="acl2014", doc_type="json"):
        self.sim_docs = {}
        self.list_ids = []
        try:
            self.es = Elasticsearch()
            self.index = index
            self.doc_type = doc_type
            # get all ids
            self.list_ids = self.getAllDocsByIndex()
        except Exception as e:
            print('Error connection with elasticsearch')
            sys.exit(1)

    def getSimDocFromCorpus(self, doc_id=None, v=[], score_folder=ConstantValues.ACL_SCORES):
        if doc_id is None:
            return None
        file_name = score_folder + "/" + doc_id + ".json"
        file_path = Path(file_name)
        if file_path.exists():
            json_data = json.load(io.open(file_name, 'r', encoding='utf-8'))
            file_doc_id = json_data['info']['id']
            if file_doc_id == doc_id:
                return json_data['score']
            else:
                # if not same id
                return None
        return None

    # def createListFiles(self, v=[], score_folder = ConstantValues.ACL_SCORES):
    #     list_files = []
    #     if v is None:
    #         return list_files
    #     for doc_id in v:
    #         list_files.append(score_folder + "/" + doc_id + ".json")
    #     return list_files

    def addDocScore(self, doc_score=None, v=None):
        if id is None:
            return
        assert (type(doc_score) == SimilairtyScores)
        if doc_score.score is None:
            # calculate new
            print("%s need to calculate new" % doc_score.id)
            doc_score.score = self.findSimDocsById(doc_id=doc_score.id)
            score = {}
            sum_score = 0.0
            for doc_id in v:
                if doc_id in doc_score.score:
                    score[doc_id] = doc_score.score[doc_id]
                    sum_score += score[doc_id]
                else:
                    score[doc_id] = 0.0
            score[ConstantValues.OneVsRest] = sum_score
            self.sim_docs[doc_score.id] = score
        else:
            self.sim_docs[doc_score.id] = doc_score.score

    # calculate similarity matrix between 2 documents
    def calSimDocs(self, v=None, pool=None):
        if v is None:
            return {}

        # list_files = self.createListFiles(v=v)

        # count_new = 0
        # count = 0

        if not pool:
            # print(mp.cpu_count())
            pool = mp.Pool(int(.5 * mp.cpu_count()))
        str_ids = (str(f) for f in v)
        for doc_score in pool.imap_unordered(SimilairtyScores, str_ids):
            # count += 1
            self.addDocScore(doc_score, v)
            # get previous calculation
            # doc_score = self.getSimDocFromCorpus(doc_id=doc_id, v=v)

            # print(docId + " - "+str(len(score_doc)))
            # score_doc[ConstantValues.OneVsRest] = 0.0
            # simdocs[docId][] = 0.0
            # sum_scores = 0.0
            # sum of scores with others in v
            # for doc_id2 in v:
            #     if (doc_id2 != doc_id) & (doc_id2 in doc_score):
            #         sum_scores += doc_score[doc_id2]
            #
            # doc_score[ConstantValues.OneVsRest] = sum_scores
            # sim_docs[doc_id] = doc_score

        # return sim_docs

    # get document similarity of docId -> {id, score}
    def findSimDocsById(self, doc_id=None):
        print(doc_id)
        if doc_id is None:
            return {}
        sim_doc = {}
        res_from = 0
        res_size = 1000
        MAXSIZE = 23000

        while res_from < MAXSIZE:
            response = self.es.search(
                index=self.index,
                body={
                    "query": {
                        "more_like_this": {
                            'fields': ["info.title", "sections.text", "sections.heading"],
                            "like": [
                                {"_index": self.index,
                                 "_type": self.doc_type,
                                 "_id": doc_id
                                 }
                            ],
                        }
                    },
                    "stored_fields": [],
                    "from": res_from,
                    "size": res_size
                },
                request_timeout=90
            )
            # print(response['hits']['total'])
            for hit in response['hits']['hits']:
                # print(hit['_id']+" "+str(hit.get('_score', 0.0)))
                # print(v)
                sim_doc[hit['_id']] = hit.get('_score', 0.0)

            res_from += res_size
            if res_from >= response['hits']['total']:
                break

        # request = Search().query(MoreLikeThis(like={'_id': id, '_index': self.index, '_type': self.doc_type},
        #                         fields=['info.title', 'sections']))
        # response = request.execute()
        # print(response)
        # print(response['hits']['total'])
        # print(hit['_score'])
        # scale score into [0,1]
        # max_score = 0.0
        # for (docid, score) in simdoc.items():
        #     simdoc[docid] = score / max_score
        return sim_doc

    def getAllDocsByIndex(self):
        request = Search(using=self.es, index=self.index, doc_type=self.doc_type).params(
            request_timeout=ConstantValues.TIMEOUT)
        response = request.scan()
        idList = []
        for hit in response:
            if "acl" in hit.meta.id:
                idList.append(hit.meta.id)
        # self.list_ids = idList
        return idList

    def removeIdNoInfor(self, v):
        newV = []
        for docId in v:
            if docId in self.list_ids:
                newV.append(docId)
        return newV

    def getRawDocById(self, id=None):
        if (id == None):
            return ""
        try:
            res = self.es.get(index=self.index, doc_type=self.doc_type, id=id)
            doc = res['_source']
        except Exception as e:
            # print('Not found doc at : '+id)
            return ""
            # sys.exit(1)
        # print(doc)
        rawtext = ""
        try:
            title = doc['info']['title']
            rawtext += title + "\n"
            sections = doc['sections']
            # print(sections)
            for sec in sections:
                # print(sec)
                if "heading" in sec:
                    rawtext += sec['heading'] + "\n"
                if "text" in sec:
                    for line in sec['text']:
                        rawtext += line
                    rawtext += "\n"

        except Exception as e:
            print('Error get information of docId: ' + id)
            return ""

        return rawtext

    def getReflist(self, id=None):
        if id == None:
            return []
        res = self.es.get(index=self.index, doc_type=self.doc_type, id=id)
        # print(res['_source'].get('references',[]))
        return res['_source'].get('references', [])

    def getDocsByAuthors(self, authors=[], year=10000, articleId=None):
        resDocs = []
        for author in authors:
            auDocs = self.searchDocsByAuthor(author=author, year=year)
            for docId in auDocs:
                # print(docId)
                if (docId != articleId):
                    reflist = self.getReflist(id=docId)
                    # print(len(reflist))
                    for refid in reflist:
                        if refid not in resDocs:
                            resDocs.append(refid)
        return resDocs

    def searchDocsByAuthor(self, author=None, year=0):
        if author == None:
            return []
        # print(author)
        res = self.es.search(index=self.index, body={"query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "info.authors.keyword": author
                        }
                    }
                ],
            }
        },
            "from": 0,
            "size": 1000})
        # print("Got %d Hits:" % res['hits']['total'])
        resultsDocs = []
        # print(res['hits']['hits'])
        for h in res['hits']['hits']:
            hit = h['_source']
            # print(hit)
            retri = RetrievedInformation(hit)
            hyear = retri.getYear()
            hid = retri.getId()
            if hyear <= year:
                if hid not in resultsDocs:
                    resultsDocs.append(hid)
                # print('%s with year %i returned with score %f' % (
                #     h.meta.id, h.info.year, h.meta.score))

        return resultsDocs

    def searchDocsByTitle(self, query="survey"):

        res = self.es.search(index=self.index, body={
            "query": {
                "bool": {
                    "must": [
                        {"multi_match": {
                            "query": query,
                            "fields": ["info.title"]

                        }}
                    ],
                }
            },
            "stored_fields": []
        })
        # print("Got %d Hits:" % res['hits']['total'])
        resultsDocs = []
        # print(res['hits']['hits'])
        for hit in res['hits']['hits']:
            # print(hit)
            resultsDocs.append(hit['_id'])
            # print('%s with year %i returned with score %f' % (
            #     h.meta.id, h.info.year, h.meta.score))

        return resultsDocs

    def getTermVector(self, docid=None):
        vector = self.es.termvectors(index=self.index, doc_type=self.doc_type, id=docid)
        print(vector)
        return vector

    # get relevant documents based on concept list
    def getRelevantDocsByCL(self, conceptlist={}, year=10000, max_each_matches=50):
        # key = id, value = similarity score
        vDocs = {}
        for query in conceptlist.keys():
            print(query)
            resDocs = self.queryByDSL(query=query, year=year, budget=max_each_matches)
            # update to vDocs
            for docId, score_sim in resDocs.items():
                if docId in vDocs:
                    # vDocs[docId] = vDocs[docId] + 1.0*score_sim*score_cl
                    vDocs[docId] = vDocs[docId] + score_sim
                else:
                    # vDocs[docId] = 1.0*score_sim*score_cl
                    vDocs[docId] = score_sim
        return vDocs

    def queryByDSL(self, query="", year=10000, budget=50):
        # fil = Q('range', body=' { "info.year": { "lte": 2000 }} ')
        query_bool = []
        query_bool.append(Q('multi_match', query=query, fields=['info.title', 'sections.text', 'sections.heading']))
        query_bool.append({'range': {'info.year': {'lte': year}}})
        q = Q({'bool': {'must': query_bool}})
        # filter = Q()
        # r = Range({ "@info.year": { "lte": 2010 }})
        # print(self.index)
        # print(self.doc_type)
        s = Search(using=self.es, index=self.index, doc_type=self.doc_type).query(q)
        # s.highlight_options(order='score')
        # s.exclude('range', fileds='info.year', lte=year)
        # s.filter(filter)
        # print(q)
        # s.query(q)
        # print("query DSL count: "+str(s.count()))
        # response = s.scan()
        # 10000 = max window
        # res = s.scan()
        print(s.count())
        if s.count() < budget:
            budget = s.count() - 1
        response = s[:budget].execute()
        # res2 = s.scan()

        # print(h)
        # print(response)
        # count=0
        selectedDocs = {}
        for h in response:
            if h.info.year <= year:
                selectedDocs[h.meta.id] = h.meta.score
                # print('%s with year %i returned with score %f' % (
                #     h.meta.id, h.info.year, h.meta.score))
            # if (len(selectedDocs)>=budget):
            #     return selectedDocs
        # for h in res2:
        #     print(h.meta.id)
        #     print(h.meta.score)
        return selectedDocs

        # print(response.__sizeof__())
        # for h in response:
        #     print(h.info.id)
        # return response

    def queryByURL(self, query="", year=10000, budget=5000):
        selectedDocs = {}
        res_from = 0
        res_size = 1000
        MAXSIZE = 23000

        while (selectedDocs.__len__() < budget) & (res_from < MAXSIZE):
            response = self.es.search(
                index=self.index,
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"multi_match": {
                                    "query": query,
                                    "fields": ["info.title", "sections.text", "sections.heading"]

                                }}
                            ],
                            "filter": [
                                {"range": {"info.year": {"lte": year}}}
                            ]
                        }
                    },
                    "stored_fields": [],
                    "from": res_from,
                    "size": res_size,
                }
            )

            # print(response)
            # print(response['hits']['total'])
            for hit in response['hits']['hits']:
                # if hit['_id'] not in selectedDocs.keys():
                selectedDocs[hit['_id']] = hit['_score']
            res_from += res_size
            if res_from >= response['hits']['total']:
                break
            # print(len(selectedDocs.items()))

        return selectedDocs


if __name__ == '__main__':
    esexport = ElasticsearchExporter(index=ConstantValues.ACL_CORPUS_INDEX, doc_type=ConstantValues.ACL_CORPUS_DOCTYPE)
    # sc.queryByDSL(index="acl2014", queryStr="concept-to-text generation", year=2000)
    # sc.getTermVector(index="acl2014", doc_type="json", docid="acl-A00-1001")
    # esexport.searchDocsByAuthor(author="Ioannis Konstas", year=2010)
    # resDocs = esexport.queryByURL(query="Machine Translation of Very Close Languages", year=2010, budget=1000)
    # resDocs = esexport.queryByDSL(query="Machine Translation of Very Close Languages", year=2010, budget=1000)
    # esexport.getRawDocById(id="acl-C08-2022")

    # res = esexport.searchDocsByTitle(query="survey")
    # print(res)
    v = esexport.getAllDocsByIndex()
    print(esexport.findSimDocsById())
    # results = esexport.queryByURL(query="Improved Models of Distortion Cost for Statistical Machine Translation",
    #                               year=2010, budget=10000)
    # listv = []
    # for docId, score in results.items():
    #     listv.append(docId)
    # print(listv)
    # simdoc = esexport.calSimDocs(v=listv)
    # print(simdoc)
    # print(len(resDocs))
    # print(resDocs)
