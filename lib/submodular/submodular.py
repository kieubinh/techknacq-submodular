#Author: Binh Kieu Th
#Target: submodular functions for generating reading lists
#mmr: Maximal Marginal Relevance
#crl: Maximal Concept Relevance
#qfr: Query-Focused Relevance
#upr: Update Relevance


from lib.submodular.constantvalues import ConstantValues
from lib.submodular.similarityscore import SimilarityScores
from lib.submodular.relevantdocuments import RelevantDocuments
import json

# from conceptgraph import ConceptGraph
# from readinglist import ReadingList
# from constantvalues import ConstantValues

class Submodular:

    def __init__(self):
        self.docs=[]
        self.id_docs=[]
        self.docsims=[]

    def loadFromList(self, readinglist):
        releventDocs = RelevantDocuments()
        releventDocs.loadFromList(readinglist)
        self.docs = releventDocs.getRelevantDocs()
        #print(readinglist)
        #self.Lambda = Lambda

    def loadFromCorpus(self, relevantdocs):
        self.docs = relevantdocs.getRelevantDocs()
        #print(self.docs)

    def getSubmodular(self, alg=ConstantValues.LAZY_GREEDY_ALG, Lambda=1.0, method="mmr", type_sim = "title"):
        #load score
        # if (type_sim=="text"):
        #     with open(ConstantValues.DOCSIMS, 'r', encoding="utf-8") as fin:
        #         jsonDocSims = json.loads(fin.read())
        #         self.id_docs=jsonDocSims['id']
        #         self.docsims = jsonDocSims['docsims']
        #         print(len(self.id_docs))
        if alg==ConstantValues.LAZY_GREEDY_ALG:
            return self.lazyGreedyAlg(self.docs, Lambda, method, type_sim)
        else:
            return None #other alg

    def lazyGreedyAlg(self, v, Lambda, method, type_sim):
        #all elements
        #selected set
        g=[]
        #remaining set
        u=[]
        for doc in v:
            u.append(doc)
        #print("BUDGET: "+str(budget))
        while len(u)>0 and len(g)<ConstantValues.BUDGET:
            dock, maxK = self.findArgmax(g, u, v, Lambda, method, type_sim)
            #print("dock: "+dock['title'])
            #if (maxK>0):
            g.append(dock)
            #u.remove(dock)
            for i in range(len(u)):
                if u[i]==dock:
                    #print("remove dock: "+str(dock))
                    u.pop(i)
                    break
            print("len: "+str(len(g))+" "+str(len(u)))
        return g

    #switch respective method
    def calMethod(self, g, v, Lambda, method, type_sim):
        result = 0.0
        if method==ConstantValues.Maximal_Marginal_Relevance:
            result = self.calMMR(g, v, Lambda, type_sim)
        if method==ConstantValues.Maximal_Concept_Relevance:
            result = self.calMCR(g, v, Lambda, type_sim)
        if method==ConstantValues.Query_Focused_Relevance:
            result = self.calQFR(g, v, Lambda, type_sim)

        return result

    def findArgmax(self, g, u, v, Lambda, method, type_sim):
        bound=self.calMethod(g, v, Lambda, method, type_sim)
        print("bound: "+str(bound))
        maxF = None
        argmax = None
        for doc in u:
            t=[]
            for x in g:
                t.append(x)
            t.append(doc)
            ft=self.calMethod(t, v, Lambda, method, type_sim)

            if (maxF==None or maxF<ft):
                maxF=ft
                argmax=doc

        print("find max: " + str(maxF))
        return argmax, maxF-bound

    def calConceptSum(self, s):
        fcover = 0.0
        for doc in s:
            jsondoc = json.loads(doc)
            fcover += float(jsondoc['score'])
        return fcover

    # add general relevance
    #default = title
    def calGeneralSum(self, s, v, type_sim="title"):
        fcover = 0.0
        if (type_sim=="text"):
            for doc1 in s:
                jsondoc1 = json.loads(doc1)
                # print(jsondoc1)
                #not consider wiki
                if 'wiki' in jsondoc1['info']['id']:
                    continue
                for doc2 in v:
                    if (doc2 not in s):
                        jsondoc2 = json.loads(doc2)
                        # not consider wiki
                        if 'wiki' in jsondoc2['info']['id']:
                            continue
                        indexDoc2 = jsondoc2['info']['id']
                        # print("doc1: "+str(indexDoc1)+" - doc2: "+str(indexDoc2))
                        fcover+=jsondoc1['scores'][indexDoc2]
            return fcover

        for doc1 in s:
            for doc2 in v:
                if (doc2 not in s):
                    jsondoc1 = json.loads(doc1)
                    jsondoc2 = json.loads(doc2)
                    fcover+= SimilarityScores(jsondoc1[type_sim], jsondoc2[type_sim]).getScore()
        return fcover

    # add query relevance
    def calQuerySum(self, s):
        fquery = 0.0
        for doc in s:
            jsondoc = json.loads(doc)
            fquery+= float(jsondoc['query_score'])
        return fquery

    # subtract relevant selected elements
    def calPenaltySum(self, s, type_sim="title"):
        fpenalty = 0.0
        if (type_sim=="text"):
            for doc1 in s:
                jsondoc1 = json.loads(doc1)
                if 'wiki' in jsondoc1['info']['id']:
                    continue
                # indexDoc1 = self.id_docs.index(jsondoc1['id'])
                for doc2 in s:
                    if (doc1 != doc2):
                        jsondoc2 = json.loads(doc2)
                        if 'wiki' in jsondoc2['info']['id']:
                            continue
                        indexDoc2 = jsondoc2['info']['id']
                        fpenalty+=jsondoc1['scores'][indexDoc2]
            return fpenalty

        for doc1 in s:
            for doc2 in s:
                if (doc1 != doc2):
                    jsondoc1 = json.loads(doc1)
                    jsondoc2 = json.loads(doc2)
                    fpenalty += SimilarityScores(jsondoc1[type_sim], jsondoc2[type_sim]).getScore()

        return fpenalty

    #Submodular functions

    #function 1: Maximal Marginal Relevance
    def calMMR(self, s, v, Lambda, type_sim="title"):
        # fcover=0.0
        # #print(str(len(s))+' - '+str(len(v)))
        # for doc1 in s:
        #     for doc2 in v:
        #         #print(str(doc2['title'])+ " "+str(doc2 in s))
        #         if (doc2 not in s):
        #             fcover+= SimilarityScores(doc1['title'], doc2['title']).getScore()
        # fpenalty = 0.0
        # for doc1 in s:
        #     for doc2 in s:
        #         if (doc1 != doc2):
        #             fpenalty+= SimilarityScores(doc1['title'], doc2['title']).getScore()
        fcover = self.calGeneralSum(s, v, type_sim)
        fpenalty = self.calPenaltySum(s, type_sim)
        return fcover - Lambda * fpenalty

    #function 2: Maximal Concept Relevance
    def calMCR(self, s, v, Lambda, type_sim="title"):
        # fcover=0.0
        # #print(str(len(s))+' - '+str(len(v)))
        # for doc1 in s:
        #     for doc2 in v:
        #         #print(str(doc2['title'])+ " "+str(doc2 in s))
        #         if (doc2 not in s):
        #             fcover+= SimilarityScores(doc1['title'], doc2['title']).getScore()
        # fpenalty = 0.0
        # for doc1 in s:
        #     for doc2 in s:
        #         if (doc1 != doc2):
        #             fpenalty+= SimilarityScores(doc1['title'], doc2['title']).getScore()
        fcover = self.calConceptSum(s)
        fpenalty = self.calPenaltySum(s, type_sim)
        return fcover - Lambda * fpenalty

    #function 3: Query-Focused Relevance
    def calQFR(self, s, v, Lambda, type_info="title"):
        fcover = self.calGeneralSum(s, v, type_info)
        fquery = self.calQuerySum(s)
        #subtract penalty
        fpenalty = self.calPenaltySum(s, type_info)
        return fcover+fquery-Lambda*fpenalty


