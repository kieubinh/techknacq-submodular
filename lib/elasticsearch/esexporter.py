import sys
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from lib.submodular.retrievedinfo import RetrievedInformation

# from elasticsearch_dsl.query import MultiMatch, Match

class ElasticsearchExporter:
    def __init__(self, index="acl2014", doc_type="json"):
        try:
            self.es=Elasticsearch()
            self.index = index
            self.doc_type = doc_type
            #get all ids
            self.getAllDocsByIndex()
        except Exception as e:
            print('Error connection with elasticsearch')
            sys.exit(1)

    def getAllDocsByIndex(self):
        request = Search(using=self.es, index=self.index, doc_type=self.doc_type)
        response = request.scan()
        idList = []
        for hit in response:
            if "acl" in hit.meta.id:
                idList.append(hit.meta.id)
        self.idList = idList

    def removeIdNoInfor(self, v):
        newV = []
        for docId in v:
            if docId in self.idList:
                newV.append(docId)
        return newV

    def getRawDocById(self, id=None):
        if (id==None):
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
            rawtext+=title+"\n"
            sections = doc['sections']
            # print(sections)
            for sec in sections:
                # print(sec)
                if "heading" in sec:
                    rawtext+=sec['heading']+"\n"
                if "text" in sec:
                    for line in sec['text']:
                        rawtext+=line
                    rawtext+="\n"

        except Exception as e:
            print('Error get information of docId: '+id)
            return ""

        return rawtext


    def getReflist(self, id=None):
        if id==None:
            return []
        res = self.es.get(index=self.index, doc_type=self.doc_type, id=id)
        # print(res['_source'].get('references',[]))
        return res['_source'].get('references',[])

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
        if author==None:
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
        resultsDocs =[]
        # print(res['hits']['hits'])
        for h in res['hits']['hits']:
            hit = h['_source']
            # print(hit)
            retrie = RetrievedInformation(hit)
            hyear = retrie.getYear()
            hid = retrie.getId()
            if hyear<=year:
                if hid not in resultsDocs:
                    resultsDocs.append(hid)
                # print('%s with year %i returned with score %f' % (
                #     h.meta.id, h.info.year, h.meta.score))

        return resultsDocs

    def getTermVector(self, docid=None):
        vector = self.es.termvectors(index=self.index, doc_type=self.doc_type, id=docid)
        print(vector)
        return vector

    def queryByDSL(self,query="", year=10000, budget=50):
        # fil = Q('range', body=' { "info.year": { "lte": 2000 }} ')
        query_bool = []
        query_bool.append(Q('multi_match', query=query, fields=['info.title', 'sections.text', 'sections.heading']))
        query_bool.append({'range': {'info.year': {'lte': year}}})
        q = Q({'bool': {'must':query_bool}})
        # filter = Q()
        # r = Range({ "@info.year": { "lte": 2010 }})
        s = Search(using=self.es, index=self.index, doc_type=self.doc_type).query(q)
        # s.highlight_options(order='score')
        # s.exclude('range', fileds='info.year', lte=year)
        # s.filter(filter)
        # print(q)
        # s.query(q)
        print(s.count())
        # response = s.scan()
        #10000 = max window
        response = s[:budget].execute()
        # res2 = s.scan()

        # print(h)
        # print(response)
        # count=0
        selectedDocs = {}
        for h in response:
            if h.info.year<=year:
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

    def queryByURL(self, query="", year=10000, budget=10000):
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
                "stored_fields": []
            }
        )

        # print(response)
        print(response['hits']['total'])
        for hit in response['hits']['hits']:
            print(hit['_score'])

if __name__ == '__main__':
    esexport = ElasticsearchExporter(index="acl2014", doc_type="json")
    # sc.queryByDSL(index="acl2014", queryStr="concept-to-text generation", year=2000)
    # sc.getTermVector(index="acl2014", doc_type="json", docid="acl-A00-1001")
    # esexport.searchDocsByAuthor(author="Ioannis Konstas", year=2010)
    # resDocs = esexport.queryByURL(query="Machine Translation of Very Close Languages", year=2010, budget=1000)
    # resDocs = esexport.queryByDSL(query="Machine Translation of Very Close Languages", year=2010, budget=1000)
    esexport.getRawDocById(id="acl-C08-2022")
    # print(len(resDocs))
    # print(resDocs)
