#tf-idf
#concept scores

from lib.submodular.constantvalues import ConstantValues
from lib.techknacq.corpus import Corpus
from nltk.tokenize import word_tokenize
import json
import numpy as np

#We will use a library in Python called gensim.
#import gensim
#print(dir(gensim))
from gensim import corpora, models, similarities
from operator import itemgetter

class RelevantDocuments:

    def __init__(self):
        self.relevantlist = []
        self.rankedTfidf = []
        self.docs = []

    def getRelevantDocs(self):
        return self.relevantlist

    def getRelevantDocsByYear(self, year=10000):
        relevantlist = []
        for doc in self.relevantlist:
            jsondoc = json.loads(doc)
            # print(jsondoc)
            # print(jsondoc['info'].get('year','0'))
            if int(jsondoc['info'].get('year','0'))<=year:
                relevantlist.append(doc)
        return relevantlist

    def loadFromList(self, readinglist):
        for doc in readinglist:
            #print(doc)
            jsondoc = self.readinglist2Json(doc, abstract=True)
            self.relevantlist.append(jsondoc)

    def scroreTfIdfModel(self, path_raw=ConstantValues.ACL, path_score=ConstantValues.ACL_SCORES):
        from time import time
        t0=time()
        corpus = Corpus(path=path_raw)
        id_documents, raw_documents = corpus.getRawDocs()
        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in raw_documents]
        dictionary = corpora.Dictionary(gen_docs)
        raw_corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
        tfidf = models.TfidfModel(raw_corpus)  # step 1 -- initialize a model
        corpus_tfidf = tfidf[raw_corpus]

        index = similarities.MatrixSimilarity(corpus_tfidf)
        docsims = index[corpus_tfidf]
        for i in range(len(id_documents)):
            doci=corpus.docs.get(id_documents[i])
            #json: "scores":{
            # "ACL-xxx":0.53,"ACL-xx2":0.43,...
            # }
            #
            dict_scores={}
            for j in range(len(id_documents)):
                namej=id_documents[j]
                dict_scores[namej]=docsims[i][j]
            # print(type(doci))
            #doci['scores']=dict_scores
            # jsondoci = self.dict2Json(doci, abstract=False)
            def myconverter(o):
                if isinstance(o, np.float32):
                    return float(o)
            with open(path_score+id_documents[i]+".json", 'w', encoding='utf-8') as fout:
                json.dump(self.scores2Json(doci, scores=dict_scores), fout, default=myconverter)
            fout.close()


    def trainTfIdfModel(self, path_raw=None, path_model="tmp/"):
        from time import time
        t0 = time()

        corpus = Corpus(path=path_raw)
        #calculate TF-IDF similarity matrix of a complete corpus with Gensim
        # STEP 1 : Compile corpus and dictionary - Index and vectorize
        id_documents, raw_documents = corpus.getRawDocs()
        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in raw_documents]
        dictionary = corpora.Dictionary(gen_docs)
        dictionary.save(path_model+ConstantValues.DICTIONARY)
        # compile corpus (vectors number of times each elements appears)
        raw_corpus = [dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
        #raw_corpus = [dictionary.doc2bow(t) for t in raw_documents]
        corpora.MmCorpus.serialize(path_model+ConstantValues.CORPUS, raw_corpus) # store to disk
        #STEP 2 : Transform and compute similarity between corpuses
        #dictionary = corpora.Dictionary.load('tmp/acl.dict')
        #corpus = corpora.MmCorpus('tmp/acl.mm')
        #Transform text with tf-idf
        tfidf = models.TfidfModel(raw_corpus)  # step 1 -- initialize a model
        corpus_tfidf = tfidf[raw_corpus]
        #STEP 3 : Create similarity matrix of all files
        index = similarities.MatrixSimilarity(corpus_tfidf)
        index.save(path_model+ConstantValues.TFIDF_INDEX)
        #index = similarities.MatrixSimilarity.load('/tmp/tfidf.index')
        #self.sims = index[corpus_tfidf]
        docsims = index[corpus_tfidf].tolist()
        #print(type(docsims))
        jsonDocSims = {
            'id':id_documents,
            'docsims':docsims
        }
        #print(jsonDocSims)
        with open(ConstantValues.DOCSIMS, 'w', encoding='utf-8') as fout:
            json.dump(jsonDocSims, fout)
        fout.close()

        print("Done in %.3fs" % (time() - t0))

    def loadFromPath(self, path=None, year=10000):
        # Let's create some documents.
        # raw_documents = ["I'm taking the show on the road.",
        #                 "My socks are a force multiplier.",
        #             "I am the barber who cuts everyone's hair who doesn't cut their own.",
        #             "Legend has it that the mind is a mad monkey.",
        #            "I make my own fun."]

        #read corpus and calculate tf-idf
        corpus = Corpus(path=path, year=year)
        self.docs = corpus.docs
        # print(self.docs['acl-P10-2049'].title)
        self.id_documents, self.raw_documents = corpus.getRawDocs()

        # print(self.id_documents)
        print("Number of documents:", self.docs.__len__())

        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in self.raw_documents]
        # print(len(gen_docs))

        # #fix for docs
        # gen_docs = [[w.lower() for w in word_tokenize(doc.text())]
        #             for id, doc in self.docs.items()]
        #
        # for id, doc in self.docs.items():
        #     gen_doc=[]
        #     for w in word_tokenize(doc.text()):
        #         gen_doc.append(w.lower())
        #     gen_docs.insert(i=id, x=gen_doc)

        # print(gen_docs[0])

        # We will create a dictionary from a list of documents. A dictionary maps every word to a number.
        self.dictionary = corpora.Dictionary(gen_docs)

        #print(self.dictionary[5])
        # print(dictionary.token2id['road'])
        print("Number of words in dictionary:", len(self.dictionary))
        # for i in range(len(dictionary)):
        #     print(i, dictionary[i])

        # Now we will create a corpus. A corpus is a list of bags of words. A bag-of-words representation for a document just lists the number of times each word occurs in the document.
        self.bagofwords = [self.dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
        #print(bagofwords)

        # Now we create a tf-idf model from the corpus. Note that num_nnz is the number of tokens.
        self.tf_idf = models.TfidfModel(self.bagofwords)
        # print(tf_idf)
        # s = 0
        # for i in bagofwords:
        #     s += len(i)
        # print(s)

        # Now we will create a similarity measure object in tf-idf space.
        # tf-idf stands for term frequency-inverse document frequency. Term frequency is how often the word shows up in the document and inverse document fequency scales the value by how rare the word is in the corpus.
        self.sims = similarities.Similarity('tmp/', self.tf_idf[self.bagofwords],
                                              num_features=len(self.dictionary))
        # print(sims)
        # print(type(sims))

    def loadFromTfIdfModel(self, path_raw, path_model="tmp/"):
        corpus = Corpus(path=path_raw)
        self.docs = corpus.docs
        self.id_documents, self.raw_documents = corpus.getRawDocs()
        self.dictionary = corpora.Dictionary.load(path_model+ConstantValues.DICTIONARY)
        self.bagofwords = corpora.MmCorpus(path_model+ConstantValues.CORPUS)
        self.tf_idf = models.TfidfModel(self.bagofwords)  # step 1 -- initialize a model
        #calculate document similarity
        corpus_tfidf = self.tf_idf[self.bagofwords]
        # index = similarities.MatrixSimilarity.load(path_model+ConstantValues.TFIDF_INDEX)
        # self.docsims = index[corpus_tfidf]
        self.sims = similarities.Similarity(path_model, corpus_tfidf, num_features=len(self.dictionary))
        # index = similarities.MatrixSimilarity.load(path_model+ConstantValues.TFIDF_INDEX)
        # self.docsims = index[self.tf_idf[self.bagofwords]]tfidf = models.TfidfModel(raw_corpus)  # step 1 -- initialize a model

        # #STEP 3 : Create similarity matrix of all files
        # index = similarities.MatrixSimilarity(corpus_tfidf)
        # # index.save(path_model+ConstantValues.TFIDF_INDEX)
        # #index = similarities.MatrixSimilarity.load('/tmp/tfidf.index')
        # #self.sims = index[corpus_tfidf]
        # docsims = index[corpus_tfidf].tolist()
        #
        # # print(type(docsims))
        # jsonDocSims = {
        #     'id': self.id_documents,
        #     'docsims': docsims
        # }
        # # print(jsonDocSims)
        # with open(ConstantValues.DOCSIMS, 'w', encoding='utf-8') as fout:
        #     json.dump(jsonDocSims, fout)
        # fout.close()

    def findRankedTfIdf(self, query):
        #We will use NLTK to tokenize.
        #A document will now be a list of tokens.

        #Now create a query document and convert it to tf-idf.
        query_doc=[]
        for keyword in query:
            for w in word_tokenize(keyword):
                query_doc.append(w.lower())
        print(query_doc)
        query_doc_bow = self.dictionary.doc2bow(query_doc)
        # print(query_doc_bow)
        query_doc_tf_idf = self.tf_idf[query_doc_bow]
        #print(query_doc_tf_idf)

        #We show an array of document similarities to query. We see that the second document is the most similar with the overlapping of socks and force.
        #print(self.sims)
        scores={}
        for i in range(len(self.sims[query_doc_tf_idf])):
            scores[self.id_documents[i]]=self.sims[query_doc_tf_idf][i]

        rankedTuple = sorted(scores.items(), key=lambda x: x[1], reverse = True)
        # print(rankedTuple)
        for id, score in rankedTuple:
            releventDoc = self.convert2Json(self.docs.get(id), query_score=score)
            #print(releventDoc)
            self.relevantlist.append(releventDoc)

    def readinglist2Json(self, doc, abstract=False):
        """Return a JSON string representing the document."""
        if (abstract):
            str_abstract=""
            para = doc.get('abstract',[])
            for sentence in para:
                str_abstract+=sentence
            doc['abstract']=str_abstract
        cvdoc= {
            'info':{
                'id': doc.get('id',''),
                'authors': doc.get('authors',[]),
                'title': doc.get('title',''),
                'year': doc.get('year',''),
                'book': doc.get('book',''),
                'url': doc.get('url',''),
                'abstract': doc.get('abstract', ''),
            },
            'references': doc.get('references',[]),
            'score':doc.get('score',0.0)
            # 'sections':doc.sections,
            # 'scores':scores
        }

        return json.dumps(cvdoc, indent=2, sort_keys=True, ensure_ascii=False)

    def scores2Json(self, doc, scores=None):
        # ACL corpus
        # abstract=""
        # # print(doc.sections[0])
        # for section in doc.sections:
        #
        #     if 'heading' in section:
        #         heading = section['heading']
        #         if (heading!=None):
        #             heading = heading.lower()
        #             texts = section['text']
        #             if "abstract" in heading:
        #                 for sentence in texts:
        #                     abstract += sentence
        #
        #                 break
        # # print(abstract)
        return {
            'info':{
                'id': doc.id,
                'authors': doc.authors,
                'title': doc.title,
                'year': doc.year,
                'book': doc.book,
                'url': doc.url,
                'abstract':doc.abstract
            },
            'references': sorted(list(doc.references)),
            'sections':doc.sections,
            'scores':scores
        }

    def convert2Json(self, doc, query_score=None):
        """Return a JSON string representing the document."""
        #ACL corpus
        cvdoc = {
            'info':{
                'id': doc.id,
                'authors': doc.authors,
                'title': doc.title,
                'year': doc.year,
                'book': doc.book,
                'url': doc.url,
                'abstract': doc.abstract,
            },
            'references': sorted(list(doc.references)),
            'sections':doc.sections,
            'scores':doc.scores
        }

        if query_score != None:
            cvdoc['query_score'] = float(query_score)

        return json.dumps(cvdoc, indent=2, sort_keys=True, ensure_ascii=False)

    def getTopResults(self, num_top = 50, method="tfidf"):

        if method=="tfidf":
            if len(self.relevantlist)<num_top:
                return self.relevantlist
            else:
                return self.relevantlist[:num_top]

        return self.relevantlist

    def getResultsByThreshold(self, threshold=0.01, method="tfidf"):
        top_results = []
        if method == "tfidf":
            for entry in self.relevantlist:
                jsonEntry = json.loads(entry)
                #print(jsonEntry['query_score'])
                if float(jsonEntry['query_score']) < threshold:
                    return top_results
                top_results.append(entry)

        return top_results

