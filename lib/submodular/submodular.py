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

    #as paper
    def mmrCal(self, s,v, Lambda):
        if ConstantValues.SIMILARITY_MEASUE=='title':
            return self.mmrCal4Title(s, v, Lambda)
        elif ConstantValues.SIMILARITY_MEASUE=='abstract':
            return self.mmrCal4Abstract(s, v, Lambda)

    #concept reading list
    def crlCal(self, s,v, Lambda):
        if ConstantValues.SIMILARITY_MEASUE=='title':
            return self.crlCal4Title(s, v, Lambda)
        elif ConstantValues.SIMILARITY_MEASUE=='abstract':
            return self.crlCal4Abstract(s, v, Lambda)

    def crlCal4Title(self,s, v, Lambda):
        fcover = 0
        # print(str(len(s))+' - '+str(len(v)))
        for doc in s:
            fcover+=doc['score']
        fpenalty = 0
        for doc1 in s:
            for doc2 in s:
                if (doc1 != doc2):

                    fpenalty += SimilarityScores(doc1['title'], doc2['title']).getScore()
        return fcover - Lambda * fpenalty

    def crlCal4Abstract(self, s, v, Lambda):
        fcover = 0.0
        # print(str(len(s))+' - '+str(len(v)))
        for doc in s:
            fcover+=doc['score']
        fpenalty = 0.0
        count=0
        for doc1 in s:
            for doc2 in s:
                if (doc1 != doc2):
                    abstract1 = ""
                    abstract2 = ""
                    for sentence in doc1['abstract']:
                        abstract1 += sentence
                    for sentence in doc2['abstract']:
                        abstract2 += sentence
                    fpenalty += SimilarityScores(abstract1, abstract2).getScore()
                    count+=1
        if count==0:
            count=1
        #return fcover - Lambda * (fpenalty/count)
        return fcover - Lambda * fpenalty

    def mmrCal4Abstract(self, s, v, Lambda):
        fcover = 0.0
        # print(str(len(s))+' - '+str(len(v)))
        for doc1 in s:
            for doc2 in v:
                # print(str(doc2['title'])+ " "+str(doc2 in s))
                if (doc2 not in s):
                    abstract1=""
                    abstract2=""
                    for sentence in doc1['abstract']:
                        abstract1+=sentence
                    for sentence in doc2['abstract']:
                        abstract2+=sentence
                    #print("abstract1 : \n" + abstract1 + " \n abstract2: \n " + abstract2)
                    fcover += SimilarityScores(abstract1, abstract2).getScore()
        fpenalty = 0.0
        for doc1 in s:
            for doc2 in s:
                if (doc1 != doc2):
                    abstract1 = ""
                    abstract2 = ""
                    for sentence in doc1['abstract']:
                        abstract1 += sentence
                    for sentence in doc2['abstract']:
                        abstract2 += sentence
                    #print("abstract1 : \n" + abstract1 + " \n abstract2: \n " + abstract2)
                    fpenalty += SimilarityScores(abstract1, abstract2).getScore()

        return fcover - Lambda * fpenalty

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
    def calPenaltySum(self, s, type_info="title"):
        fpenalty=0.0
        for doc1 in s:
            for doc2 in s:
                if (doc1 != doc2):
                    jsondoc1 = json.loads(doc1)
                    jsondoc2 = json.loads(doc2)
                    fpenalty += SimilarityScores(jsondoc1[type_info], jsondoc2[type_info]).getScore()

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


