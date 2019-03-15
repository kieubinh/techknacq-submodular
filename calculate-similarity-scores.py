

def calSim():
    from lib.submodular.constantvalues import ConstantValues
    from lib.submodular.relevantdocuments import RelevantDocuments
    relevantDocs = RelevantDocuments()
    relevantDocs.scroreTfIdfModel(path_raw=ConstantValues.ACL, path_score=ConstantValues.ACL_SCORES)

def testImporter():
    from lib.elasticsearch.serverimporter import ServerImporter
    ServerImporter().jsonParser("data/acl/")

if __name__ == '__main__':
    testImporter()
    # calSim()

# ServerImporter().jsonParser("data/acl/")