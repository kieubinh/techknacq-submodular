#Author: Binh Kieu Thanh
#Target:
# 1. import ACL data into elasticsearch
# 2. calculate similarity score between 2 documents
# 3. generate citation graph

import json
import os
import io
import sys
import numpy as np
# from datetime import datetime
from elasticsearch import Elasticsearch
from lib.elasticsearch.esexporter import ElasticsearchExporter

# res = es.search(index="acl", body={"query": {"match_all": {"acl"}}})
# print("Got %d Hits:" % res['hits']['total'])
# print(res)
class ElasticsearchImporter:
    def __init__(self, host="localhost", port="9200"):
        self.es = Elasticsearch([{'host': host, 'port': port}])

    #input: json document
    #output: a query in order to update into elasticsearch
    def jsonParser(self, corpusPath="data/acl/", index="acl2014", doctype="json"):
        # es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

        for root, dirs, files in os.walk(corpusPath, topdown=False):
            for nameFile in files:
                # must be json
                if "json" in nameFile:
                    # print(nameFile)
                    nameId = nameFile[:nameFile.find('.json')]
                    # print(nameId)
                    # file = open(root+"/"+nameFile, encoding="utf-8")
                    try:
                        jsondata = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                        # es.indices.create(index='acl', ignore=400)
                        print(nameId)
                        # print(jsondata)
                        self.es.index(index=index, ignore=400, doc_type=doctype, id=nameId, body=jsondata)
                        # print(res['acl'])
                    except Exception as e:
                        print('Error reading JSON document:', nameFile, file=sys.stderr)
                        print(e, file=sys.stderr)
                        sys.exit(1)

    # input: xml document
    # output: a query in order to update into elasticsearch
    def xmlParser(self, xmlDoc):
        equery=""

        return equery

    # calculate document similarity score between any 2 documents
    # and save to index = "acl_ds_score"
    def scoreDocSim(self, from_index="acl_tfidf", from_doctype="doc", to_index="acl_score", to_doctype="json"):
        ese = ElasticsearchExporter(index=from_index, doc_type=from_doctype)

        docIds = ese.getAllDocsByIndex()
        for docId in docIds:
            score_doc = ese.findSimDocsById(docId=docId, v=docIds)
            jsondict = {
                "info": {
                    "id": docId,
                    "type": "tfidf",
                    "description": "document similarity"
                },
                "score": score_doc
            }
            # jsondata = json.dumps(jsondict)
            self.es.index(index=to_index, doc_type=to_doctype, id=docId, body=jsondict)
            print(to_index+"/"+to_doctype+"/"+docId)
            # print(jsondata)


from lib.constantvalues import ConstantValues
if __name__ == '__main__':
    # ElasticsearchImporter().jsonParser(corpusPath="../../data/acl/", index="acltest3",
    #                                    doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    # ElasticsearchImporter().jsonParser(corpusPath="../../data/acl/", index=ConstantValues.ACL_CORPUS_INDEX, doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    ElasticsearchImporter().scoreDocSim()

# curl -X POST "localhost:9200/acl_tfidf/_close"
# curl -X PUT "localhost:9200/acl_tfidf/_settings" -H 'Content-Type: application/json' -d'
# {
#   "index": {
#     "similarity": {
#       "default": {
#         "type": "classic"
#       }
#     }
#   }
# }
# '
# curl -X POST "localhost:9200/acl_tfidf/_open"

# create index 'acl_tfidf' first
# PUT acl_tfidf
# {
#   "index": {
#     "similarity": {
#       "default": {
#         "type": "classic"
#       }
#     }
#   }
# }

# curl -XPUT 'localhost:9200/acl_score/_settings' -H 'Content-Type: application/json' -d'
# {
# "index" : {
# "mapping" : {
# "total_fields" : {
# "limit" : "30000"
# }
# }
# }
# }'