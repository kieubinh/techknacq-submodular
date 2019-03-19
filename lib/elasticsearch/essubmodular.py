from lib.constantvalues import ConstantValues
from lib.elasticsearch.esexporter import ElasticsearchExporter

class ElasticsearchSubmodularity:
    #calculate all query-focused relevance
    def __init__(self, index="acl2014", doc_type="json", query=None):
        self.ese = ElasticsearchExporter(index=index, doc_type=doc_type)
        if (query!=None) & (len(query) > 0):
            self.qsim = self.ese.calQuerySimilarity(query)
        else:
            self.qsim = {}

    def calDocumentSimilarity(self, index="acl2014", doc_type="json"):
        docids = getAllDocs(index, doc_type)

    #s, v: list of articleId
    def calGeneralSumByText(self, s, v):

        fcover = 0.0
        for doc1 in s:
            jsondoc1 = json.loads(doc1)

            # not consider wiki
            if 'wiki' in jsondoc1['info']['id']:
                continue
            for doc2 in v:
                if (doc2 not in s):
                    jsondoc2 = json.loads(doc2)
                    # not consider wiki
                    indexDoc2 = jsondoc2['info'].get('id', '')
                    if (indexDoc2 == '') or ('wiki' in indexDoc2):
                        continue
                    if 'scores' not in jsondoc2:
                        continue
                    # if indexDoc2 in jsondoc2['scores']:
                    fcover += jsondoc1['scores'].get(indexDoc2, 0.0)
        return fcover

    #subtract relevant selected elements
    def calPenaltySumByText(self, s):
        fpenalty = 0.0
        for doc1 in s:
            jsondoc1 = json.loads(doc1)
            # print(jsondoc1)
            if 'wiki' in jsondoc1['info']['id']:
                continue
            # indexDoc1 = self.id_docs.index(jsondoc1['id'])
            for doc2 in s:
                if (doc1 != doc2):
                    jsondoc2 = json.loads(doc2)
                    indexDoc2 = jsondoc2['info'].get('id', '')
                    if (indexDoc2 == '') or ('wiki' in indexDoc2):
                        continue
                    if 'scores' not in jsondoc2:
                        continue
                    # if indexDoc2 in jsondoc2['scores']:
                    fpenalty += jsondoc1['scores'].get(indexDoc2, 0.0)

        return fpenalty

    # function 3: Query-Focused Relevance
    def calQFR(self, s, v, Lambda, type_info="text"):
        fcover = self.calGeneralSumByText(s, v, type_info)
        fquery = self.calQuerySum(s)
        # subtract penalty
        fpenalty = self.calPenaltySumByText(s, type_info)
        return fcover + fquery - Lambda * fpenalty

    #submodular algorithm
    def greedyAlgByCardinality(self, v, Lambda, method, type_sim):
        #all elements = articleId
        #selected set
        s=[]
        #remaining set
        u=[]
        #print("BUDGET: "+str(budget))
        while len(u)>0 and len(s)<ConstantValues.BUDGET:
            docidk, maxK = self.findArgmax(s, u, v, Lambda, method, type_sim)
            # print("dock: "+dock['title'])
            #if (maxK>0):
            s.append(docidk)
            #u.remove(dock)
            u.remove(docidk)
            print("len: "+str(len(s))+" "+str(len(u)))
        return s

    #switch respective method
    def calMethod(self, s, v, Lambda, method, type_sim):
        result = 0.0
        if method==ConstantValues.Query_Focused_Relevance:
            result = self.calQFR(s, v, Lambda, type_sim)
        # print(result)
        return result

    def findArgmax(self, s, u, v, Lambda, method, type_sim):
        bound=self.calMethod(s, v, Lambda, method, type_sim)
        print("bound: "+str(bound))
        maxF = None
        argmax = None
        for doc in u:
            t=[]
            for x in s:
                t.append(x)
            t.append(doc)
            ft=self.calMethod(t, v, Lambda, method, type_sim)

            if (maxF==None or maxF<ft):
                maxF=ft
                argmax=doc

        print("find max: " + str(maxF))
        return argmax, maxF-bound