#Author: Binh Kieu Th
#Target:
# 1. import ACL data into elasticsearch
# 2. calculate similarity score between 2 documents
# 3. generate citation graph

import json
import os
import io
import sys
# from datetime import datetime
from elasticsearch import Elasticsearch

# res = es.search(index="acl", body={"query": {"match_all": {"acl"}}})
# print("Got %d Hits:" % res['hits']['total'])
# print(res)
class ServerImporter:

    #input: json document
    #output: a query in order to update into elasticsearch
    def jsonParser(self, corpusPath="data/acl/"):
        es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

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
                        es.index(index='acl2014', ignore=400, doc_type='json', id=nameId, body=jsondata)
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


if __name__ == '__main__':
    ServerImporter().jsonParser("data/acl-test/")