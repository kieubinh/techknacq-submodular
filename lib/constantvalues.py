

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
    Alpha = 50.0
    Beta = 5.0
    Gamma = 25.0
    w_years = 0.5
    TEST_YEAR = 2005
    # score for relations between documents with same authors
    SCORE_SAME_AUTHORS = 2.0
    SCORE_REF_SAME_AUTHORS = 1.0

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
    Query_Author_Influence_v1 = "qai_v1"
    Query_Author_Influence_v2 = "qai_v2"
    Query_Author_Influence_v3 = "qai_v3"
    Query_Author_Influence_v11 = "qai_v11"
    Query_Author_Influence_v12 = "qai_v12"
    Maximal_Concept_Relevance = "mcr"
    Query_Focused_Relevance_v1 = "qfr_v1"
    Query_Author_NonRedundancy_v1 = "qan_v1"
    Update_Relevance = "upr"
    # similarity method
    More_Like_This  = "mlt"
    ES              = "es"
    ES_SUB          = "es-sub"
    ES_AU           = "es-au"
    ES_AU_SUB       = "es-au-sub"
    ES_AU_SUB_CG    = "es-au-sub-cg"
    ES_SUB_CG       = "es-sub-cg"
    ES_AU_SUB_TOP   = "es-au-sub-top"

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