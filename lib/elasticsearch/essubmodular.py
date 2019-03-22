from lib.constantvalues import ConstantValues
from lib.elasticsearch.esexporter import ElasticsearchExporter
from lib.submodular.similarityscore import SimilarityScores

class ElasticsearchSubmodularity:
    #calculate all query-focused relevance
    def __init__(self, esexport=None, query=None, year=10000, MAX_SIZE=1000):
        if esexport==None:
            print("No information about elasticsearch server")
            return
        self.ese = esexport
        if (query!=None) & (len(query) > 0):
            self.qsim = self.ese.queryByDSL(query=query, year= year, budget=MAX_SIZE)
        else:
            self.qsim = {}

    # def calDocumentSimilarity(self, index="acl2014", doc_type="json"):
    #     docids = getAllDocs(index, doc_type)

    def calQuerySum(self, newId=None):
        # print(newId)
        if newId in self.qsim:
            return self.qsim[newId]
        else:
            return 0.0

    #s, v: list of articleId
    #F(snew) = Sim(q, new) + Sum(new, i) - (1+lambda) * Sum(Sim(new, j)) with i belongs V\S and j!=new, j belongs S
    def calChangeCoPe(self, newId=None, s=[], v=[], Lambda=1.0):
        # add coverage
        fcc = 0.0
        # subtract relevant selected elements
        fcp = 0.0
        if newId == None:
            return 0.0
        rawdoc1 = self.ese.getRawDocById(newId)
        #if not found text
        if len(newId)<10:
            return 0.0
        # print(docId1+" : ")
        # print(rawdoc1)
        for docId2 in v:
            if (docId2!=newId):
                rawdoc2 = self.ese.getRawDocById(docId2)
                if len(rawdoc2) < 10:
                    continue
                if (docId2 in s):
                    fcp += SimilarityScores().cosineOf2Text(rawdoc1, rawdoc2)
                else:# if (docId2 in s):
                    fcc += SimilarityScores().cosineOf2Text(rawdoc1, rawdoc2)

        return fcc-(1+Lambda)*fcp

        # s, v: list of articleId
    def calChangeCoPeByEs(self, newId=None, s=[], v=[], Lambda=1.0):
        # add coverage
        fcc = 0.0
        # subtract relevant selected elements
        fcp = 0.0
        if newId == None:
            return 0.0
        docsim = self.ese.getDocSim(newId)
        # if not found any similar doc
        if len(docsim) < 1:
            return 0.0
        # print(docId1+" : ")
        for docId2 in v:
            if (docId2 != newId):
                #if it belongs similar document set
                if docId2 in docsim:
                    if (docId2 in s):
                        fcp += docsim[docId2]
                    else:
                        fcc += docsim[docId2]

        return fcc-(1+Lambda)*fcp

    # def calPenaltySumByText(self, newId=None, s=[]):
    #
    #     if newId==None:
    #         return fpenalty
    #     rawdoc1 = self.ese.getRawDocById(newId)
    #     if len(rawdoc1) < 10:
    #         return fpenalty
    #     for docId2 in s:
    #         if (newId != docId2):
    #             rawdoc2 = self.ese.getRawDocById(docId2)
    #             if len(rawdoc2)<10:
    #                 continue
    #             fpenalty += SimilarityScores().cosineOf2Text(rawdoc1, rawdoc2)
    #
    #     return fpenalty

    # function 3: Query-Focused Relevance
    # only calculate change when add newId
    def calQFR(self, newId, s, v, Lambda):
        #add coverage subtract penalty
        fcp = self.calChangeCoPeByEs(newId=newId, s=s, v=v, Lambda=Lambda)
        fquery = self.calQuerySum(newId)
        # print(newId+" - "+str(fquery)+" "+str(fcp))
        # subtract penalty
        # fpenalty = self.calPenaltySumByText(newId, s)
        return fquery + fcp

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
    def calMethod(self, newId, s, v, Lambda, method):
        result = 0.0
        if method==ConstantValues.Query_Focused_Relevance:
            result = self.calQFR(newId=newId, s=s, v=v, Lambda=Lambda)
        # print(result)
        return result

    def findArgmax(self, s, u, v, Lambda, method):
        # bound=self.calMethod(s, v, Lambda, method)
        # print("bound: "+str(bound))
        maxF = None
        argmax = None
        for docId in u:
            ft=self.calMethod(docId, s, v, Lambda, method)

            if (maxF==None or maxF<ft):
                maxF=ft
                argmax=docId

        print("maxF: " + str(maxF))
        print(s + [argmax])
        return argmax, maxF

if __name__ == '__main__':
    ese = ElasticsearchExporter(index="acl2014", doc_type="json")
    essub = ElasticsearchSubmodularity(esexport=ese, query="Cross-lingual Discourse Relation Analysis: A corpus study and a semi-supervised classification system", year=2014, MAX_SIZE=1000)
    essub.greedyAlgByCardinality(v=ese.getDocsByAuthors(authors=["Ani Nenkova", "Marine Carpuat"], year=2014, articleId="acl-C14-1055"), Lambda=1.0, method="qfr")
