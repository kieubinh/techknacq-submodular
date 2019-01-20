

class ConstantValues:

    # User model constants
    BEGINNER = 5
    INTERMEDIATE = 4
    ADVANCED = 3

    BUDGET=10
    PENALTY = 1.0
    #SIMILARITY_MEASUE='title'
    #SIMILARITY_MEASUE='abstract'
    SIMILARITY_MEASUE = 'text'

    LAZY_GREEDY_ALG=0 #default
    COSINE = 0 #default

    #method
    Maximal_Marginal_Relevance="mmr"
    Maximal_Concept_Relevance="mcr"
    Query_Focused_Relevance="qfr"
    Update_Relevance="upr"

    #data path
    SAMPLE="sample/"
    ACL = "data/acl"

    #save model
    DICTIONARY = "acl.dict"
    CORPUS = "acl.mm"
    TFIDF_INDEX = "tfidf.index"
    DOCSIMS = "docsims.json"