

from lib.submodular.relevantdocuments import RelevantDocuments

relevantDocs = RelevantDocuments()
relevantDocs.loadFromPath("sample/")
relevantDocs.findRankedTfIdf("concept to text")

scores = relevantDocs.getTopResults(10, "tfidf")
print(scores)

print(relevantDocs.getResultsByThreshold(0.01,"tfidf"))

