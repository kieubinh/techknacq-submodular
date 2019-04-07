
from lib.elasticsearch.esimporter import ElasticsearchImporter
from lib.constantvalues import ConstantValues
if __name__ == '__main__':
    # ElasticsearchImporter().jsonParser(corpusPath="../../data/acl/", index="acltest3",
    #                                    doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    # ElasticsearchImporter().jsonParser(corpusPath="data/acl/", index=ConstantValues.ACL_CORPUS_INDEX, doctype=ConstantValues.ACL_CORPUS_DOCTYPE)
    ElasticsearchImporter().scoreDocSimToFolder()