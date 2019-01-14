#tf-idf
#concept scores

from lib.techknacq.corpus import Corpus
from nltk.tokenize import word_tokenize

#We will use a library in Python called gensim.
import gensim
print(dir(gensim))

class RelevantDocuments:

    rankedTfidf = []
    relevantlist=[]

    def __init__(self, path=None):
        # Let's create some documents.
        # raw_documents = ["I'm taking the show on the road.",
        #                 "My socks are a force multiplier.",
        #             "I am the barber who cuts everyone's hair who doesn't cut their own.",
        #             "Legend has it that the mind is a mad monkey.",
        #            "I make my own fun."]

        #read corpus and calculate tf-idf
        corpus = Corpus(path=path)
        self.docs = corpus.docs
        self.id_documents, self.raw_documents = corpus.getRawDocs()

        #print(self.id_documents)
        print("Number of documents:", self.docs.__len__())

        gen_docs = [[w.lower() for w in word_tokenize(text)]
                    for text in self.raw_documents]
        print(len(gen_docs))

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
        self.dictionary = gensim.corpora.Dictionary(gen_docs)
        #print(self.dictionary[5])
        # print(dictionary.token2id['road'])
        print("Number of words in dictionary:", len(self.dictionary))
        # for i in range(len(dictionary)):
        #     print(i, dictionary[i])

        # Now we will create a corpus. A corpus is a list of bags of words. A bag-of-words representation for a document just lists the number of times each word occurs in the document.
        bagofwords = [self.dictionary.doc2bow(gen_doc) for gen_doc in gen_docs]
        #print(bagofwords)

        # Now we create a tf-idf model from the corpus. Note that num_nnz is the number of tokens.
        self.tf_idf = gensim.models.TfidfModel(bagofwords)
        # print(tf_idf)
        # s = 0
        # for i in bagofwords:
        #     s += len(i)
        # print(s)

        # Now we will create a similarity measure object in tf-idf space.
        # tf-idf stands for term frequency-inverse document frequency. Term frequency is how often the word shows up in the document and inverse document fequency scales the value by how rare the word is in the corpus.
        self.sims = gensim.similarities.Similarity('tmp/', self.tf_idf[bagofwords],
                                              num_features=len(self.dictionary))
        # print(sims)
        # print(type(sims))

    def findRankedTfIdf(self, query):
        #We will use NLTK to tokenize.
        #A document will now be a list of tokens.


        #Now create a query document and convert it to tf-idf.
        query_doc = [w.lower() for w in word_tokenize(query)]
        # print(query_doc)
        query_doc_bow = self.dictionary.doc2bow(query_doc)
        # print(query_doc_bow)
        query_doc_tf_idf = self.tf_idf[query_doc_bow]
        #print(query_doc_tf_idf)

        #We show an array of document similarities to query. We see that the second document is the most similar with the overlapping of socks and force.
        #print(self.sims[query_doc_tf_idf])
        scores={}
        for i in range(len(self.sims[query_doc_tf_idf])):
            scores[self.id_documents[i]]=self.sims[query_doc_tf_idf][i]

        rankedTuple = sorted(scores.items(), key=lambda x: x[1], reverse = True)
        print(rankedTuple)
        for id, score in rankedTuple:
            releventDoc = self.convert2Entry(self.docs.get(id), query_score=score)
            #print(releventDoc)
            self.relevantlist.append(releventDoc)

    def convert2Entry(self, doc, query_score=0.0):
        #print(id+" - "+doc.id)
        return {
                #"id":id,
                "doc":doc.json(),
                "query_score":query_score
        }


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
                if entry['query_score'] < threshold:
                    return top_results
                top_results.append(entry)

        return top_results
