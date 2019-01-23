from lib.submodular.constantvalues import ConstantValues
from lib.submodular.relevantdocuments import RelevantDocuments


def main():
    relevantDocs = RelevantDocuments()
    relevantDocs.scroreTfIdfModel(path_raw=ConstantValues.ACL_PART, path_score=ConstantValues.ACL_SCORES)

if __name__ == '__main__':

    main()

