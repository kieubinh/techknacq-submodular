#Author: Binh Kieu Th
#Target:
# 1. import ACL data into elasticsearch
# 2. calculate similarity score between 2 documents
# 3. generate citation graph

import json
from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])


with open("acl-A00-1002.json", 'r', encoding='utf-8') as fin:
        jsontest = json.loads(fin.read())
        # print(jsontest)
        # fout.close()

# es.indices.create(index='acl', ignore=400)
es.index(index='acl3', ignore=400, doc_type='json', id=2, body=jsontest)
# print(res['acl'])

res = es.search(index="acl2", body={"references": {"match_all": {"acl"}}})
print("Got %d Hits:" % res['hits']['total'])
print(res)


class ServerImporter:
    def __init__(self, corpusPath=None):
        self.corpus_path=corpusPath

    #input: json document
    #output: a query in order to update into elasticsearch
    def jsonParser(self, jsonDoc):
        equery=""

        return equery

    # input: xml document
    # output: a query in order to update into elasticsearch
    def xmlParser(self, xmlDoc):
        equery=""

        return equery

