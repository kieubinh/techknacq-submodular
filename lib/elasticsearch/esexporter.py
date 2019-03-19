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
        except Exception as e:
            print('Error connection with elasticsearch')
            sys.exit(1)

    def calQuerySimilarity(self, query=None):
        q = Q('bool',
              must=[Q('multi_match', query=query, fields=['info.title', 'sections.text', 'sections.heading'])])
        s = Search(using=self.es, index=self.index).query(q)
        print(s.count())
        response = s.scan()

    def getReflist(self, id=None):
        if id==None:
            return []
        res = self.es.get(index=self.index, doc_type=self.doc_type, id=id)
        print(res['_source'].get('references',[]))
        return res['_source'].get('references',[])

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
        print("Got %d Hits:" % res['hits']['total'])
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

    def queryByDSL(self,queryStr="", year=10000, budget=50):
        # fil = Q('range', body=' { "info.year": { "lte": 2000 }} ')
        q = Q('bool', must=[Q('multi_match', query=queryStr, fields=['info.title', 'sections.text', 'sections.heading'])])
        # filter = Q()
        # r = Range({ "@info.year": { "lte": 2010 }})
        s = Search(using=self.es, index=self.index).query(q)
        # s.exclude('range', fileds='info.year', lte=year)
        # s.filter(filter)
        # print(q)
        # s.query(q)
        print(s.count())
        # response = s.scan()

        response = s[:budget*6].execute()

        # print(h)
        # print(response)
        # count=0
        selectedDocs = {}
        for h in response:
            if h.info.year<=year:
                selectedDocs[h.meta.id] = h.meta.score
                # print('%s with year %i returned with score %f' % (
                #     h.meta.id, h.info.year, h.meta.score))
            if (len(selectedDocs)>=budget):
                return selectedDocs
        return selectedDocs

        # print(response.__sizeof__())
        # for h in response:
        #     print(h.info.id)
        # return response

    def queryByURL(self, queryStr="", year=10000):
        response = self.es.search(
            index=self.index,
            body={
                "query": {
                    "bool": {
                        "must": [

                            {"multi_match": {
                                "query": queryStr,
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
        for hit in response['hits']['hits']:
            print(hit['_score'], hit['_source']['info']['id'])

if __name__ == '__main__':
    esexport = ElasticsearchExporter(index="acl2014", doc_type="json")
    # sc.queryByDSL(index="acl2014", queryStr="concept-to-text generation", year=2000)
    # sc.getTermVector(index="acl2014", doc_type="json", docid="acl-A00-1001")
    esexport.searchDocsByAuthor(author="Ioannis Konstas", year=2010)

