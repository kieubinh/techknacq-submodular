from lib.constantvalues import ConstantValues
from lib.document.similarityscore import SimilarityScore
from lib.elasticsearch.esexporter import ElasticsearchExporter


class ElasticsearchSubmodularity:
    # calculate all query-focused relevance
    # def __init__(self, esexport=None, query=None, year=10000, MAX_SIZE=1000):
    #     if esexport == None:
    #         print("No information about elasticsearch server")
    #         return
    #     self.ese = esexport
    #     if (query != None) & (len(query) > 0):
    #         self.qsim = self.ese.queryByDSL(query=query, year=year, budget=MAX_SIZE)
    #     else:
    #         self.qsim = {}

    def __init__(self, esexport=None, v=None, simq=None, Lambda=None):
        if v is None:
            print("No candidate!")
            return
        if simq is None:
            simq={}
        if esexport == None:
            print("No information about elasticsearch server!")
            return
        if Lambda is None:
            self.Lambda = 1.0 - 1.0 * ConstantValues.BUDGET / max(len(v), 1)
        self.ese = esexport
        self.simq = simq
        self.v = v



    # def calDocumentSimilarity(self, index="acl2014", doc_type="json"):
    #     docids = getAllDocs(index, doc_type)

    def calDeltaQuery(self, newId=None):
        # print(newId)
        if newId in self.simq:
            return self.simq[newId]
        else:
            return 0.0

    # s, v: list of articleId
    # F(snew) = Sim(q, new) + Sum(new, i) - (1+lambda) * Sum(Sim(new, j)) with i belongs V\S and j!=new, j belongs S
    def calChangeCoPe(self, newId=None, s=[], v=[]):
        # add coverage
        fcc = 0.0
        # subtract relevant selected elements
        fcp = 0.0
        if newId == None:
            return 0.0
        rawdoc1 = self.ese.getRawDocById(newId)
        # if not found text
        if len(newId) < 10:
            return 0.0
        # print(docId1+" : ")
        # print(rawdoc1)
        for docId2 in v:
            if (docId2 != newId):
                rawdoc2 = self.ese.getRawDocById(docId2)
                if len(rawdoc2) < 10:
                    continue
                if (docId2 in s):
                    fcp += SimilarityScore().cosineOf2Text(rawdoc1, rawdoc2)
                else:  # if (docId2 in s):
                    fcc += SimilarityScore().cosineOf2Text(rawdoc1, rawdoc2)

        return fcc - (1 + self.Lambda) * fcp

    # s, v: list of articleId
    # delta_fcp(S_(k+1))    =   (1-lambda) * Sum_(x_i in V\{x_(k+1)}) sim(d_x_i, d_x_(k+1))
    #                           - (2-lambda) Sum_(x_i in S_k) sim (d_x_i, d_x_(k+1))
    def calDeltaCoveragePenalty(self, newId=None, s=[], v=[]):

        # subtract relevant selected elements

        if newId is None:
            return 0.0
        # get document similarity between one and the rest of documents
        fdck = self.simdocs[newId][ConstantValues.OneVsRest]
        # print(docId1+" : ")
        fdpk = self.calDeltaPenalty(newId=newId, s=s, v=v)

        return fdck, fdpk

    # s, v: list of articleId
    def calDeltaPenalty(self, newId=None, s=[], v=[]):
        # subtract relevant selected elements
        fcp = 0.0
        if newId is None:
            return 0.0
        # docsim = self.ese.getDocSim(newId)
        # if not found any similar doc
        # if len(docsim) < 1:
        #     return 0.0
        # print(docId1+" : ")
        for docId2 in s:
            # if (docId2 != newId):
                # if it belongs similar document set
            if docId2 in self.simdocs[newId]:
                fcp += self.simdocs[newId][docId2]

        return fcp

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

    # Vc: 300 concepts (fixed)
    # ft(S_k) = (1- lambda) * fc(S_k) - lambda * fp(S_k)
    # fc(S_k) = Sum_(c_i in Vc) Sum_(x_j in S_k) w(c_i, d_x_j)
    # fp(S_k) = Sum_(x_i in S_k) Sum_(x_j in S_k) sim (d_x_i, d_x_j)
    # delta_fc(S_(k+1)) = Sum_(c_i in Vc) w(c_i, d_x_(k+1))
    # delta_fp(S_(k+1)) = Sum_(x_i in S_k) sim(d_i, d_x_(k+1))
    def calMCR(self, newId, s, v):
        # add coverage subtract penalty
        # delta_fc = self.calDeltaCoveragePenalty(newId=newId, s=s, v=v)
        delta_fc = self.calDeltaQuery(newId)
        delta_fp = self.calDeltaPenalty(newId)
        # print(newId+" - "+str(fquery)+" "+str(fcp))
        # subtract penalty
        # fpenalty = self.calPenaltySumByText(newId, s)
        return (1 - self.Lambda) * delta_fc - self.Lambda * delta_fp

    # function 3: Query-Focused Relevance
    # only calculate change when add newId
    # ft(S_k) = (1-lambda) * fc(S_k) + alpha * fq(S_k) - lambda * fp(S_k)
    # fc(S_k) = Sum_(x_i in V\S_k) Sum_(x_j in S_k) sim (d_x_i, d_x_j)
    # fp(S_k) = Sum_(x_i in S_k) Sum_(x_j in S_k) sim (d_x_i, d_x_j)
    # fq(S_k) = Sum_(x_i in S_k) w(q, d_x_i)
    # fp(S_k) = Sum_(x_i in S_k) Sum_(x_j in S_k) sim (d_x_i, d_x_j)
    # delta_fc(S_(k+1))     =   Sum_(x_i in V\{x_(k+1)}) sim(d_x_i, d_x_(k+1))
    #                           - 2 * Sum_(x_i in S_k) sim(d_x_i, d_x_(k+1))
    # delta_fp(S_(k+1))     =   Sum_(x_i in S_k) sim(d_x_i, d_x_(k+1))
    # delta_fcp(S_(k+1))    =   (1-lambda) * Sum_(x_i in V\{x_(k+1)}) sim(d_x_i, d_x_(k+1))
    #                           - (2-lambda) Sum_(x_i in S_k) sim (d_x_i, d_x_(k+1))
    # delta_fq(S_(k+1))     =   w(q, x_(k+1)) with x_(k+1) in S_(k+1)
    def calQFR(self, newId, s, v, alpha=ConstantValues.Alpha):

        delta_fq = self.calDeltaQuery(newId)
        # return alpha * delta_fq
        # add coverage subtract penalty
        delta_fc, delta_fp = self.calDeltaCoveragePenalty(newId=newId, s=s, v=v)
        # print(newId+" - "+str(fquery)+" "+str(fcp))
        # subtract penalty
        # fpenalty = self.calPenaltySumByText(newId, s)
        # print(alpha, Lambda)
        # print(newId+" - coverage: "+str(delta_fc)+" , penalty: "+str(delta_fp)+" , query: "+str(delta_fq))
        alpha = 1.0 * alpha * len(v)
        beta = 1.0-self.Lambda
        gamma = 2.0-self.Lambda
        # print(alpha, beta, gamma)
        # print(delta_fq, delta_fc, delta_fp)
        return alpha * delta_fq + beta * delta_fc - gamma * delta_fp

    # submodular algorithm
    def greedyAlgByCardinality(self, method):
        # remove no information first
        v = self.ese.removeIdNoInfor(self.v)
        # if the number of elements in V <= BUDGET -> get all elements in v
        # if len(v) <= ConstantValues.BUDGET:
        #     return v
        self.simdocs = self.ese.calSimDocs(v)
        print("V: " + str(len(v)) + " -> (submodular function) -> BUDGET = " + str(ConstantValues.BUDGET))
        # all elements = articleId
        # selected set
        s = []
        # remaining set
        u = []
        for docid in v:
            u.append(docid)
        # print("BUDGET: "+str(budget))
        while len(u) > 0 and len(s) < ConstantValues.BUDGET:
            docidk, maxK = self.findArgmax(s, u, v, method)
            # print("dock: "+dock['title'])
            # if (maxK>0):
            s.append(docidk)
            # u.remove(dock)
            u.remove(docidk)
            print("len: " + str(len(s)) + " " + str(len(u)))
        return s

    # switch respective method
    def calMethod(self, newId, s, v, method):
        result = 0.0
        if method == ConstantValues.Query_Focused_Relevance:
            result = self.calQFR(newId=newId, s=s, v=v)
        elif method == ConstantValues.Maximal_Concept_Relevance:
            result = self.calMCR(newId=newId, s=s, v=v)
        # print(result)
        return result

    def findArgmax(self, s, u, v, method):
        # bound=self.calMethod(s, v, method)
        # print("bound: "+str(bound))
        maxF = None
        argmax = None
        for docId in u:
            ft = self.calMethod(docId, s, v, method)

            if (maxF == None or maxF < ft):
                maxF = ft
                argmax = docId

        print("max delta F: " + str(maxF))
        print(s + [argmax])
        return argmax, maxF


if __name__ == '__main__':
    ese = ElasticsearchExporter(index="acl2014", doc_type="json")
    simq = ese.queryByDSL(query="Cross-lingual Discourse Relation Analysis: A corpus study and a semi-supervised classification system",
                                       year=2014, budget=1000)
    essub = ElasticsearchSubmodularity(esexport=ese, v=ese.getDocsByAuthors(authors=["Ani Nenkova", "Marine Carpuat"], year=2014, articleId="acl-C14-1055"),
                                       simq=simq, Lambda=None)
    essub.greedyAlgByCardinality(method="qfr")
