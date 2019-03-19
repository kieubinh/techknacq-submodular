
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from lib.submodular.retrievedinfo import RetrievedInformation

# from elasticsearch_dsl.query import MultiMatch, Match

class ServerConnecter:
    def __init__(self):
        self.es=Elasticsearch()

    def getReflist(self, index="acl2014", doc_type="json", id=None):
        if id==None:
            return []
        res = self.es.get(index=index, doc_type=doc_type, id=id)
        print(res['_source'].get('references',[]))
        return res['_source'].get('references',[])

    def searchDocsByAuthor(self, index="acl2014", author=None, year=0):
        if author==None:
            return []
        # print(author)
        res = self.es.search(index=index, body={"query": {
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

    def getTermVector(self, index="acl2014", doc_type="json", docid=None):
        vector= self.es.termvectors(index=index, doc_type=doc_type, id=docid)
        print(vector)
        return vector

    def queryByDSL(self, index="acl2014",queryStr="", year=10000, budget=50):
        # fil = Q('range', body=' { "info.year": { "lte": 2000 }} ')
        q = Q('bool', must=[Q('multi_match', query=queryStr, fields=['info.title', 'sections.text', 'sections.heading'])])
        # filter = Q()
        # r = Range({ "@info.year": { "lte": 2010 }})
        s = Search(using=self.es, index=index).query(q)
        # s.exclude('range', fileds='info.year', lte=year)
        # s.filter(filter)
        print(q)
        # s.query(q)
        # print(s.count())
        # response = s.scan()

        response = s[:budget*4].execute()

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

    def queryByURL(self, index="acl2014",queryStr="", year=10000):
        response = self.es.search(
            index=index,
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
                }
            }
        )

        # print(response)
        for hit in response['hits']['hits']:
            print(hit['_score'], hit['_source']['info']['id'])

if __name__ == '__main__':
    sc = ServerConnecter()
    # sc.queryByDSL(index="acl2014", queryStr="concept-to-text generation", year=2000)
    # sc.getTermVector(index="acl2014", doc_type="json", docid="acl-A00-1001")
    sc.searchDocsByAuthor(index="acl2014", author="Ioannis Konstas", year=2010)

