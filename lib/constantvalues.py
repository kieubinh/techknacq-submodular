

class ConstantValues:

    # User model constants
    BEGINNER = 5
    INTERMEDIATE = 4
    ADVANCED = 3

    TIMEOUT = 10
    MAX_LENGTH_QUERY = 900

    MAX_SUBMODULARITY = 23000
    MAXSIZE = 23000
    BUDGET = 100
    # Lambda = 0.5
    Alpha = 10.0
    Beta = 1.0
    Gamma = 5.0
    w_years = 0.5
    #SIMILARITY_MEASUE='title'
    #SIMILARITY_MEASUE='abstract'
    SIMILARITY_MEASUE = 'text'
    # ACL_CORPUS_INDEX = "acl_tfidf"
    ACL_CORPUS_INDEX = "acl_bm25"
    ACL_CORPUS_DOCTYPE = "doc"
    OneVsRest = "OneVsRest"

    LAZY_GREEDY_ALG=0 #default
    COSINE = 0 #default

    # submodular method
    Maximal_Marginal_Relevance_v1 = "mmr_v1"
    Maximal_Marginal_Relevance_v2 = "mmr_v2"
    Maximal_Marginal_Relevance_v3 = "mmr_v3"
    Diversity_Reward_Function_v1 = "drf_v1"
    Diversity_Reward_Function_v2 = "drf_v2"
    Maximal_Concept_Relevance = "mcr"
    Query_Focused_Relevance = "qfr"
    Update_Relevance = "upr"
    # similarity method
    More_Like_This  = "mlt"
    ES              = "es"
    ES_QFR          = "es-qfr"
    ES_AU           = "es-au"
    ES_AU_QFR       = "es-au-qfr"
    ES_AU_QFR_CG    = "es-au-qfr-cg"
    ES_QFR_CG       = "es-qfr-cg"
    ES_AU_QFR_TOP   = "es-au-qfr-top"

    #data path
    SAMPLE="sample/"
    ACL = "../data/acl/"
    ACL_PART = "../data/acl-part/"
    # ACL_SCORES = "../data/acl-score/"
    ACL_SCORES = "../data/acl-bm25-score/"
    # SAMPLE_SCORES = "sample-bm25-score/"

    #save model
    DICTIONARY = "acl.dict"
    CORPUS = "acl.mm"
    TFIDF_INDEX = "tfidf.index"
    DOCSIMS = "docsims.json"

    #evaluation
    OUTPUT_KEY = "output"
    ANSWER_KEY = "references"