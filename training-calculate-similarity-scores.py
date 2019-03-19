from lib.elasticsearch.esimporter import ServerImporter
from lib.constantvalues import ConstantValues
from lib.submodular.relevantdocuments import RelevantDocuments

def calSim():
    relevantDocs = RelevantDocuments()
    relevantDocs.scroreTfIdfModel(path_raw=ConstantValues.ACL, path_score=ConstantValues.ACL_SCORES)

def testImporter():
    ServerImporter().jsonParser("data/acl/")

if __name__ == '__main__':
    testImporter()
    # calSim()

# ServerImporter().jsonParser("data/acl/")