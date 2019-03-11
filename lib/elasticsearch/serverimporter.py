#Author: Binh Kieu Th
#Target:
# 1. import ACL data into elasticsearch
# 2. calculate similarity score between 2 documents
# 3. generate citation graph


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

