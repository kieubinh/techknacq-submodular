# Author: Binh Kieu Thanh
# Target:
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
from lib.constantvalues import ConstantValues


# res = es.search(index="acl", body={"query": {"match_all": {"acl"}}})
# print("Got %d Hits:" % res['hits']['total'])
# print(res)
class ElasticsearchImporter:
    def __init__(self, host="localhost", port="9200"):
        self.es = Elasticsearch([{'host': host, 'port': port, 'timeout': 90}])

    # input: json document
    # output: a query in order to update into elasticsearch
    def jsonParser(self, corpusPath="data/acl/", index="acl2014", doctype="json"):
        # es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])
        print(corpusPath)
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
        equery = ""

        return equery

    # calculate document similarity score between any 2 documents
    # and save to index = "acl_ds_score"
    def scoreDocSim(self, from_index="acl_tfidf", from_doctype="doc", to_index="acl_score", to_doctype="json"):
        ese = ElasticsearchExporter(index=from_index, doc_type=from_doctype)
        to_ese = ElasticsearchExporter(index=to_index, doc_type=to_doctype)

        all_doc_ids = ese.get_all_ids_of_corpus()
        done_doc_ids = to_ese.get_all_ids_of_corpus()
        # ignore docs which have already calculated similarity score with other documents
        # for done_id in done_doc_ids:
        #     if done_id in doc_ids:
        #         doc_ids.remove(done_id)

        print("calculate similarity score of %d documents" % (len(all_doc_ids) - len(done_doc_ids)))
        for doc_id in all_doc_ids:
            # ignore docs which have already calculated similarity score with other documents
            if doc_id not in done_doc_ids:
                score_doc = ese.findSimDocsById(doc_id=doc_id)
                jsondict = {
                    "info": {
                        "id": doc_id,
                        "type": "tfidf",
                        "description": "document similarity"
                    },
                    "score": score_doc
                }
                # jsondata = json.dumps(jsondict)
                self.es.index(index=to_index, doc_type=to_doctype, id=doc_id, body=jsondict)
                print(to_index + "/" + to_doctype + "/" + doc_id)
            # print(jsondata)

    def loadListDocIds(self, to_folder="data/acl-score/"):
        if to_folder is None:
            print("Not found folder!")
            return []
        done_doc_ids = []
        for root, dirs, files in os.walk(to_folder, topdown=False):
            for name_file in files:
                if "json" in name_file:
                    doc_id = name_file.replace(".json", "")
                    done_doc_ids.append(doc_id)
        return done_doc_ids

    # calculate document similarity score between any 2 documents
    # and save as files to folder data/acl_score/
    def scoreDocSimToFolder(self, from_index="acl_tfidf", from_doctype="doc", to_folder=ConstantValues.ACL_SCORES):
        ese = ElasticsearchExporter(index=from_index, doc_type=from_doctype)
        all_doc_ids = ese.get_all_ids_of_corpus()
        done_doc_ids = self.loadListDocIds(to_folder)
        # print(done_doc_ids)

        print("calculate similarity score of %d documents " % (len(all_doc_ids) - len(done_doc_ids)))
        count = 0
        for doc_id in all_doc_ids:
            # ignore docs which have already calculated similarity score with other documents
            if doc_id not in done_doc_ids:
                score_doc = ese.findSimDocsById(doc_id=doc_id)
                jsondict = {
                    "info": {
                        "id": doc_id,
                        "type": "bm25",
                        "description": "document similarity",
                        "size": score_doc.__len__()
                    },
                    "score": score_doc
                }

                def myconverter(o):
                    if isinstance(o, np.float32):
                        return float(o)

                with open(to_folder + doc_id + ".json", 'w', encoding='utf-8') as fout:
                    json.dump(jsondict, fout, default=myconverter)
                fout.close()
                count += 1
                print("(%d / %d) wrote to file %s"
                      % (count, len(all_doc_ids)-len(done_doc_ids), to_folder + doc_id + ".json"))


from lib.constantvalues import ConstantValues

if __name__ == '__main__':
    # ElasticsearchImporter().jsonParser(corpusPath=ConstantValues.SAMPLE, index=ConstantValues.ACL_CORPUS_INDEX,
    #                                    doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    # ElasticsearchImporter().jsonParser(corpusPath=ConstantValues.ACL, index=ConstantValues.ACL_CORPUS_INDEX, doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    ElasticsearchImporter().scoreDocSimToFolder(from_index=ConstantValues.ACL_CORPUS_INDEX,
                                                from_doctype=ConstantValues.ACL_CORPUS_DOCTYPE, to_folder=ConstantValues.SAMPLE_SCORES)

