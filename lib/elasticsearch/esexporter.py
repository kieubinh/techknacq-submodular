import sys
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from lib.submodular.articleinfo import ArticleInformation
from lib.constantvalues import ConstantValues
from lib.utils import Utils


# from elasticsearch_dsl.query import MultiMatch, Match
# from elasticsearch_dsl.query import MoreLikeThis


class ElasticsearchExporter:
    def __init__(self, index="acl_bm25", doc_type="json"):
        self.idList = []
        try:
            self.es = Elasticsearch()
            self.index = index
            self.doc_type = doc_type
            # get all ids
            self.get_all_ids_of_corpus()
        except Exception as e:
            print('Error connection with elasticsearch')
            sys.exit(1)

    def cal_cite_net(self, v=None, year=0):
        # return: influence score = number of citations / number of years until 2012 (test set)
        cite_to = {}
        if v is None:
            return cite_to

        for doc_id in v:
            cite_to[doc_id] = self.find_id_from_references(doc_id=doc_id, year=year)
            # print(cite_to[doc_id])
            # doc_year = self.get_year_by_id(id=doc_id)
            # print(doc_count, doc_year, year)
            # inf_score[doc_id] = 1.0 * doc_count / (year - doc_year)

        return cite_to

    def calSimDocs(self, v=None):
        # return: calculate similarity matrix between 2 documents
        if v is None:
            return {}
        sim_docs = {}
        count_new = 0
        count = 0
        print(len(v))
        for doc_id in v:
            count += 1
            # get previous calculation
            doc_score = Utils.getSimDocFromCorpus(doc_id=doc_id)
            if doc_score is None:
                # calculate new
                count_new += 1
                print("%s need to calculate new (%d / %d)" % (doc_id, count_new, count))
                doc_score = self.findSimDocsById(doc_id=doc_id)
            # print(docId + " - "+str(len(score_doc)))
            # score_doc[ConstantValues.OneVsRest] = 0.0
            # simdocs[docId][] = 0.0
            sum_scores = 0.0
            # sum of scores with others in v
            matrix_score = {}
            for doc_id2 in v:
                if (doc_id2 != doc_id) and (doc_id2 in doc_score):
                    matrix_score[doc_id2] = doc_score[doc_id2]
                    sum_scores += doc_score[doc_id2]

            matrix_score[ConstantValues.OneVsRest] = sum_scores
            sim_docs[doc_id] = matrix_score

        return sim_docs

    def find_id_from_references(self, doc_id=None, year=ConstantValues.TEST_YEAR):
        # print(doc_id)
        if doc_id is None:
            return {}

        cite_docs = {}
        res_from = 0
        res_size = 1000

        while res_from < ConstantValues.MAXSIZE:

            response = self.es.search(index=self.index, body=
            {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {
                                    "references.keyword": doc_id
                                }
                            }
                        ],
                        "filter": [
                            {"range": {"info.year": {"lt": year}}}
                        ]
                    }
                },

                "stored_fields": [],
            },
                                      request_timeout=90
                                      )
            # print(response['hits']['total'])
            for hit in response['hits']['hits']:
                # print(hit['_id'] + " " + str(hit.get('_score', 0.0)))
                cite_docs[hit['_id']] = hit.get('_score', 0.0)
            res_from += res_size
            if res_from >= response['hits']['total']:
                break

        return cite_docs

    def findSimDocsById(self, doc_id=None):
        # return: document similarity of docId -> {id, score}
        print(doc_id)
        if doc_id is None:
            return {}
        sim_doc = {}
        res_from = 0
        res_size = 1000

        while res_from < ConstantValues.MAXSIZE:
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

    def get_all_ids_of_corpus(self):
        # return: id list of corpus
        request = Search(using=self.es, index=self.index, doc_type=self.doc_type).params(
            request_timeout=ConstantValues.TIMEOUT)
        response = request.scan()
        idList = []
        for hit in response:
            if "acl" in hit.meta.id:
                idList.append(hit.meta.id)
        self.idList = idList
        return idList

    def removeIdNoInfor(self, v):
        newV = []
        for docId in v:
            if docId in self.idList:
                newV.append(docId)
        return newV

    def getRawDocById(self, id=None):
        if id == None:
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

    def get_year_by_id(self, id=None):
        # return: year of doc id

        if id is None:
            return ""
        try:
            res = self.es.get(index=self.index, doc_type=self.doc_type, id=id)
            doc = res['_source']
        except Exception as e:
            print('Not found doc at: ' + id)
            return 0
            # sys.exit(1)

        try:
            year = doc['info']['year']
        except Exception as e:
            print('Error get information year of doc id: ' + id)
            return 0

        return year

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
                if docId != articleId:
                    reflist = self.getReflist(id=docId)
                    # print(len(reflist))
                    for refid in reflist:
                        if refid not in resDocs:
                            resDocs.append(refid)
        return resDocs

    def searchDocsByAuthor(self, author=None, year=0):
        # return all papers with same author in authors
        if author is None:
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
            retri = ArticleInformation(hit)
            hyear = retri.getYear()
            hid = retri.getId()
            if hyear < year:
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

    # lte = less than or equal
    # lt = less than
    def queryByDSL(self, query="", year=10000, budget=50):
        # fil = Q('range', body=' { "info.year": { "lt": 2000 }} ')
        query_bool = []
        query_bool.append(Q('multi_match', query=query, fields=['info.title', 'sections.text', 'sections.heading']))
        query_bool.append({'range': {'info.year': {'lt': year}}})
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
            budget = s.count()
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

        while (res_from < budget) & (res_from < ConstantValues.MAXSIZE):
            if res_size + res_from > budget:
                res_size = budget - res_from
            try:
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
                                    {"range": {"info.year": {"lt": year}}}
                                ]
                            }
                        },
                        "stored_fields": [],
                        "from": res_from,
                        "size": res_size,
                    }
                )
            except Exception as e:
                print('Error queryByURL: from %i to %i' % (res_from, res_size), file=sys.stderr)
                print(e, file=sys.stderr)
                return None

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
    v = esexport.get_all_ids_of_corpus()
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
