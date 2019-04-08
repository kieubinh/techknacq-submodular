
from lib.elasticsearch.esimporter import ElasticsearchImporter
from lib.constantvalues import ConstantValues
if __name__ == '__main__':
    # ElasticsearchImporter().jsonParser(corpusPath="../../data/acl/", index="acltest3",
    #                                    doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    # ElasticsearchImporter().jsonParser(corpusPath="../data/acl/", index=ConstantValues.ACL_CORPUS_INDEX, doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    ElasticsearchImporter().scoreDocSimToFolder()


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
#
# curl -XPUT 'localhost:9200/acl_score/_settings' -H 'Content-Type: application/json' -d'
# {
#   "index.max_result_window" : "30000"
# }'

# curl -XPUT 'localhost:9200/acl_tfidf/_settings' -H 'Content-Type: application/json' -d'
# {
#   "index.max_result_window" : "30000"
# }'
