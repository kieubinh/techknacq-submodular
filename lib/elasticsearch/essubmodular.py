import math

from lib.constantvalues import ConstantValues
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

    def __init__(self, ese=None, v=None, simq={}, authors_score={}, year=0):
        if v is None:
            print("No candidate!")
            return

        if ese is None:
            print("No information about elasticsearch server!")
            return

        # remove no information first
        self.v = ese.removeIdNoInfor(v)
        # if the number of elements in V <= BUDGET -> get all elements in v
        # if len(v) <= ConstantValues.BUDGET:
        #     return v
        self.simdocs = ese.calSimDocs(v)
        self.cite_to = ese.cal_cite_net(v, year=year)
        self.authors_score = authors_score
        print("V: " + str(len(v)) + " -> (submodular function) -> BUDGET = " + str(ConstantValues.BUDGET))
        self.ese = ese
        self.simq = simq

        # def calDocumentSimilarity(self, index="acl2014", doc_type="json"):
        #     docids = getAllDocs(index, doc_type)

    # submodular algorithm
    def greedyAlgByCardinality(self, method=ConstantValues.Maximal_Concept_Relevance, Lambda=0.0):

        # all elements = articleId
        # selected set
        s = []
        # remaining set
        u = []
        for docid in self.v:
            u.append(docid)
        # print("BUDGET: "+str(budget))
        print("Lambda: " + str(Lambda))
        rank = ConstantValues.BUDGET
        result = {}
        while len(u) > 0 and len(s) < ConstantValues.BUDGET:
            docidk, maxK = self.findArgmax(s=s, u=u, method=method, Lambda=Lambda)
            # print(docidk)
            # print(maxK)
            # if no else better
            if maxK < 0:
                break
            s.append(docidk)
            result[docidk] = rank
            rank -= 1
            # u.remove(dock)
            u.remove(docidk)
            # print("len: " + str(len(s)) + " " + str(len(u)))

        return result

    def findArgmax(self, s, u, method, Lambda=0.0):
        # bound=self.calMethod(s, v, method)
        # print("bound: "+str(bound))
        maxF = None
        argmax = None
        for docId in u:
            ft = self.calMethod(docId, s, method, Lambda=Lambda)

            if (maxF is None) or (maxF < ft):
                maxF = ft
                argmax = docId

        # print("max delta F: " + str(maxF))
        # print(s + [argmax])
        return argmax, maxF

    # switch respective method
    def calMethod(self, newId, s, method, Lambda=0.0):
        result = 0.0
        if method == ConstantValues.Query_Focused_Relevance:
            result = self.funcQFR(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Maximal_Concept_Relevance:
            result = self.funcMCR(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Maximal_Marginal_Relevance_v1:
            result = self.funcMMRv1(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Maximal_Marginal_Relevance_v2:
            result = self.funcMMRv2(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Maximal_Marginal_Relevance_v3:
            result = self.funcMMRv3(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Diversity_Reward_Function_v1:
            result = self.funcDRFv1(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Diversity_Reward_Function_v2:
            result = self.funcDRFv2(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Query_Author_Influence_v1:
            result = self.funcQAIv1(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Query_Author_Influence_v2:
            result = self.funcQAIv2(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Query_Author_Influence_v11:
            result = self.funcQAIv11(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Query_Author_Influence_v12:
            result = self.funcQAIv12(newId=newId, s=s, Lambda=Lambda)
        elif method == ConstantValues.Query_Author_Influence_v3:
            result = self.funcQAIv3(newId=newId, s=s, Lambda=Lambda)

        # print(result)
        return result

    def calSimQuery(self, new_id=None):
        # return sim(newId, q)
        # print(newId)
        if new_id in self.simq:
            return self.simq[new_id]
        else:
            return 0.0

    def calAuthorsScore(self, new_id=None):
        # return number of citations / number of years until test set year (2012)
        if new_id in self.authors_score:
            return self.authors_score[new_id]
        else:
            return 0.0

    def calInfluenceScore(self, new_id=None):
        # return number of citations / number of years until test set year (2012)
        new_year = self.ese.get_year_by_id(new_id)
        if new_id is None:
            return 0.0
        return len(self.cite_to[new_id]) * 1.0 / (ConstantValues.TEST_YEAR - new_year)

    def calDivQuery(self, new_id, s=[]):
        # return Sum of Sqrt( Sum of rj) with j in Pi and S
        score_p = {}
        for doc_id in s:
            part_doc = doc_id[4]
            # print(part_doc)
            if part_doc not in score_p:
                score_p[part_doc] = 0.0
            score_p[part_doc] += self.calSimQuery(doc_id)
        # cal new_id
        if new_id[4] not in score_p:
            score_p[new_id[4]] = self.calSimQuery(new_id)
        else:
            score_p[new_id[4]] += self.calSimQuery(new_id)
        # cal sum
        sum_div = 0.0
        for part, score in score_p.items():
            if score > 0:
                sum_div += math.sqrt(score)

        return sum_div

    def calDeltaCoPen(self, newId=None, s=[]):

        # s, v: list of articleId
        # delta_fcp(S_(k+1))    =   (1-lambda) * Sum_(x_i in V\{x_(k+1)}) sim(d_x_i, d_x_(k+1))
        #                           - (2-lambda) Sum_(x_i in S_k) sim (d_x_i, d_x_(k+1))

        if newId is None:
            return 0.0
        # get document similarity between one and the rest of documents
        fdck = self.simdocs[newId][ConstantValues.OneVsRest]
        # print(docId1+" : ")
        fdpk = self.calDeltaPenalty(newId=newId, s=s)

        return fdck, fdpk

    def calDeltaCoverage(self, newId=None):
        if newId is None:
            return 0.0
        return self.simdocs[newId][ConstantValues.OneVsRest]

    def calDeltaPenalty(self, newId=None, s=[]):
        # s, v: list of articleId
        # delta_penalty = Sum of Sim(newId, dxi) with all dxi in s

        fdp = 0.0
        if newId is None:
            return 0.0

        for docId in s:
            if docId in self.simdocs[newId]:
                fdp += self.simdocs[newId][docId]

        return fdp

    def calMaxPenalty(self, newId, s):
        # subtract maximum relevant selected elements
        fmp = 0.0
        if newId is None:
            return 0.0
        for docId in s:
            if docId in self.simdocs[newId]:
                fmp = max(fmp, self.simdocs[newId][docId])

        return fmp

    def calAvgPenalty(self, newId, s):
        # subtract average of relevant selected elements
        fdp = 0.0
        if newId is None:
            return 0.0

        for docId in s:
            if docId in self.simdocs[newId]:
                fdp += self.simdocs[newId][docId]
        # add one to avoid ZeroDivision
        return (fdp+1.0) / (len(s)+1.0)

    # ------------------------------------------- SUBMODULAR FUNCTIONS -------------------------------------------------

    def funcMMRv1(self, newId, s, Lambda=1.0):
        # Maximum marginal relevance version 1
        # Lambda *Sim1 (sk, q) - (1-Lambda) max Sim2(si, sk)

        delta_fp = self.calMaxPenalty(newId=newId, s=s)
        delta_fq = self.calSimQuery(newId)

        # print(newId+" - "+str(fquery)+" "+str(fcp))
        # subtract penalty
        # fpenalty = self.calPenaltySumByText(newId, s)
        return Lambda * delta_fq - (1 - Lambda) * delta_fp

    def funcMMRv2(self, newId, s=None, Lambda=1.0):
        # Maximum marginal relevance version 2
        # Lambda * Sim1(sk, q) - (1-Lambda) Sum Sim2(si, sk)

        delta_fp = self.calAvgPenalty(newId, s=s)
        delta_fq = self.calSimQuery(newId)

        # print("Lambda: %.2f, delta_fq: %.2f, delta_fp: %.2f" % (Lambda, delta_fq, delta_fp))
        return Lambda * delta_fq - (1 - Lambda) * delta_fp

    def funcMMRv3(self, newId, s=None, Lambda=1.0):
        # Maximum marginal relevance version 2
        # Lambda * Sim1(sk, q) - (1-Lambda) Sum Sim2(si, sk)

        delta_fp = self.calMaxPenalty(newId, s=s)
        delta_fq = self.calSimQuery(newId)

        # print("Lambda: %.2f, delta_fq: %.2f, delta_fp: %.2f" % (Lambda, delta_fq, delta_fp))
        return Lambda * delta_fq + (1 - Lambda) * delta_fp

    def funcDRFv1(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_finf = self.calInfluenceScore(new_id=newId)
        delta_fd = self.calDivQuery(new_id=newId, s=s)

        # print("Lambda: %.2f, delta_fq: %.2f, delta_fp: %.2f" % (Lambda, delta_fq, delta_fp))
        return Lambda * delta_finf + (1 - Lambda) * delta_fd

    def funcDRFv2(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_fp = self.calMaxPenalty(newId=newId, s=s)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        # print("Lambda: %.2f, delta_fq: %.2f, delta_fp: %.2f" % (Lambda, delta_fq, delta_fp))
        return Lambda * delta_fq - (1 - Lambda) * delta_fp

    def funcQAIv1(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_finf = self.calInfluenceScore(new_id=newId)
        delta_fau = self.calAuthorsScore(new_id=newId)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        return ConstantValues.Alpha * delta_fau + Lambda * delta_finf + (1-Lambda) * delta_fq

    def funcQAIv11(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_finf = self.calInfluenceScore(new_id=newId)
        delta_fau = self.calAuthorsScore(new_id=newId)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        return ConstantValues.Alpha * delta_fau + ConstantValues.Beta * delta_finf + ConstantValues.Gamma * delta_fq

    def calCiteNet(self, s=None, new_id=None):
        # return: Sum of (di -> dj) with di in V-S+{new}, dj in S+{new}
        count = 0
        for doc_id in s:
            # check new_id cite doc_id or not
            if doc_id in self.cite_to[new_id]:
                count += 1

        return len(self.cite_to[new_id]) - count

    def funcQAIv2(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_finf = self.calCiteNet(s=s, new_id=newId)
        delta_fau = self.calAuthorsScore(new_id=newId)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        # return ConstantValues.Alpha*delta_fau + ConstantValues.Beta*delta_finf + ConstantValues.Gamma*delta_fq
        return ConstantValues.Alpha * delta_fau + Lambda * delta_finf + (1-Lambda) * delta_fq

    def funcQAIv12(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        delta_finf = self.calCiteNet(s=s, new_id=newId)
        delta_fau = self.calAuthorsScore(new_id=newId)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        return ConstantValues.Alpha * delta_fau + ConstantValues.Beta * delta_finf + ConstantValues.Gamma * delta_fq

    def funcQAIv3(self, newId, s=None, Lambda=1.0):
        # Diversity reward function
        # Lambda * Sum sqrt(sum rj) (j in Pi and j in S) - (1 - Lambda) * delta_fp

        # delta_finf = self.calCiteNet(s=s, new_id=newId)
        delta_fau = self.calAuthorsScore(new_id=newId)
        delta_fq = self.calDivQuery(new_id=newId, s=s)

        # return ConstantValues.Alpha*delta_fau + ConstantValues.Beta*delta_finf + ConstantValues.Gamma*delta_fq
        return Lambda * delta_fau + (1-Lambda) * delta_fq

    def funcMCR(self, newId, s, alpha=1.0, Lambda=1.0):
        # Vc: 300 concepts (fixed)
        # ft(S_k) = (1- lambda) * fc(S_k) - lambda * fp(S_k)
        # fc(S_k) = Sum_(c_i in Vc) Sum_(x_j in S_k) w(c_i, d_x_j)
        # fp(S_k) = Sum_(x_i in S_k) Sum_(x_j in S_k) sim (d_x_i, d_x_j)
        # delta_fc(S_(k+1)) = Sum_(c_i in Vc) w(c_i, d_x_(k+1))
        # delta_fp(S_(k+1)) = Sum_(x_i in S_k) sim(d_i, d_x_(k+1))

        delta_fc = self.calDeltaCoverage(newId)
        delta_fp = self.calDeltaPenalty(newId, s=s)
        delta_fq = self.calSimQuery(newId)
        alpha = 1.0 * alpha * ((len(self.v) - len(s)) * len(s))
        beta = 1.0
        gamma = 2.0 + Lambda

        return alpha * delta_fq + beta * delta_fc - gamma * delta_fp

    def funcQFR(self, newId, s, Lambda=1.0):
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

        delta_fq = self.calSimQuery(newId)

        delta_fc, delta_fp = self.calDeltaCoPen(newId=newId, s=s)
        alpha = ConstantValues.Alpha
        beta = ConstantValues.Beta * Lambda
        gamma = ConstantValues.Beta * (1-Lambda)

        # print(alpha, beta, gamma)
        # print(delta_fq, delta_fc, delta_fp)
        return alpha * delta_fq + beta * delta_fc - gamma * delta_fp


if __name__ == '__main__':
    ese = ElasticsearchExporter(index="acl2014", doc_type="json")
    simq = ese.queryByDSL(
        query="Cross-lingual Discourse Relation Analysis: A corpus study and a semi-supervised classification system",
        year=2014, budget=1000)
    essub = ElasticsearchSubmodularity(ese=ese,
                                       v=ese.getDocsByAuthors(authors=["Ani Nenkova", "Marine Carpuat"], year=2014,
                                                              articleId="acl-C14-1055"),
                                       simq=simq)
    essub.greedyAlgByCardinality(Lambda=0.5)
