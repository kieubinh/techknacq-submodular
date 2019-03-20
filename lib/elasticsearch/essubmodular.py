from lib.constantvalues import ConstantValues
from lib.elasticsearch.esexporter import ElasticsearchExporter
from lib.submodular.similarityscore import SimilarityScores

class ElasticsearchSubmodularity:
    #calculate all query-focused relevance
    def __init__(self, index="acl2014", doc_type="json", query=None, year=10000, MAX_SIZE=1000):
        self.ese = ElasticsearchExporter(index=index, doc_type=doc_type)
        if (query!=None) & (len(query) > 0):
            self.qsim = self.ese.queryByDSL(query=query, year= year, budget=MAX_SIZE)
        else:
            self.qsim = {}

    # def calDocumentSimilarity(self, index="acl2014", doc_type="json"):
    #     docids = getAllDocs(index, doc_type)

    def calQuerySum(self, s):
        fquery = 0.0
        for docId in s:
            if docId in self.qsim:
                fquery+=self.qsim[docId]
        return fquery

    #s, v: list of articleId
    def calGeneralSumByText(self, s, v):

        fcover = 0.0
        for docId1 in s:
            rawdoc1 = self.ese.getRawDocById(docId1)
            #if not found text
            if len(rawdoc1)<10:
                continue
            # print(docId1+" : ")
            # print(rawdoc1)
            for docId2 in v:
                if (docId2 not in s):
                    rawdoc2 = self.ese.getRawDocById(docId2)
                    if len(rawdoc2)<10:
                        continue
                    # print(docId2 + " : ")
                    # print(rawdoc2)
                    # if indexDoc2 in jsondoc2['scores']:
                    fcover += SimilarityScores().cosineOf2Text(rawdoc1, rawdoc2)
        return fcover

    #subtract relevant selected elements
    def calPenaltySumByText(self, s):
        fpenalty = 0.0
        for docId1 in s:
            rawdoc1 = self.ese.getRawDocById(docId1)
            if len(rawdoc1) < 10:
                continue
            for docId2 in s:
                if (docId1 != docId2):
                    rawdoc2 = self.ese.getRawDocById(docId2)
                    if len(rawdoc2)<10:
                        continue
                    fpenalty += SimilarityScores().cosineOf2Text(rawdoc1, rawdoc2)

        return fpenalty

    # function 3: Query-Focused Relevance
    def calQFR(self, s, v, Lambda):
        # fcover = self.calGeneralSumByText(s, v)
        fquery = self.calQuerySum(s)
        # subtract penalty
        fpenalty = self.calPenaltySumByText(s)
        return fquery - Lambda * fpenalty

    #submodular algorithm
    def greedyAlgByCardinality(self, v, Lambda, method):
        #remove no information first
        v = self.ese.removeIdNoInfor(v)
        print("V: "+str(len(v))+" -> (submodular function) -> BUDGET = "+str(ConstantValues.BUDGET))
        #all elements = articleId
        #selected set
        s=[]
        #remaining set
        u=[]
        for docid in v:
            u.append(docid)
        #print("BUDGET: "+str(budget))
        while len(u)>0 and len(s)<ConstantValues.BUDGET:
            docidk, maxK = self.findArgmax(s, u, v, Lambda, method)
            # print("dock: "+dock['title'])
            #if (maxK>0):
            s.append(docidk)
            #u.remove(dock)
            u.remove(docidk)
            print("len: "+str(len(s))+" "+str(len(u)))
        return s

    #switch respective method
    def calMethod(self, s, v, Lambda, method):
        result = 0.0
        if method==ConstantValues.Query_Focused_Relevance:
            result = self.calQFR(s, v, Lambda)
        # print(result)
        return result

    def findArgmax(self, s, u, v, Lambda, method):
        bound=self.calMethod(s, v, Lambda, method)
        print("bound: "+str(bound))
        maxF = None
        argmax = None
        for doc in u:
            t=[]
            for x in s:
                t.append(x)
            t.append(doc)
            ft=self.calMethod(t, v, Lambda, method)

            if (maxF==None or maxF<ft):
                maxF=ft
                argmax=doc

        print("find max: " + str(maxF))
        return argmax, maxF-bound

if __name__ == '__main__':
    essub = ElasticsearchSubmodularity(index="acl2014", doc_type="json", query="Cross-lingual Discourse Relation Analysis: A corpus study and a semi-supervised classification system", year=2014, MAX_SIZE=100)
    es = ElasticsearchExporter(index="acl2014", doc_type="json")
    essub.greedyAlgByCardinality(v=es.getDocsByAuthors(authors=["Ani Nenkova", "Marine Carpuat"], year=2014, articleId="acl-C14-1055"), Lambda=1.0, method="qfr")