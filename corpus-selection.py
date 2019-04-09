
from lib.elasticsearch.esexporter import ElasticsearchExporter
from lib.techknacq.corpus import Corpus
from lib.constantvalues import ConstantValues
import selection_corpus as ransel
import random

def getRandomDocs(listdocs=[], MAXSIZE=50):
    if len(listdocs) <= MAXSIZE:
        return listdocs
    selected = []
    while len(selected) < MAXSIZE:
        x = random.randrange(len(listdocs))
        selected.append(listdocs[x])
        # print(selected)
        # print(docs)
        listdocs.remove(listdocs[x])
    print(len(selected))
    print(selected)
    return selected


import click
@click.command()
@click.argument('path', type=click.Path(exists=True))
# @click.argument('query', nargs=-1)
def main(path="data/acl/"):
    # relevantDocs = RelevantDocuments()
    # relevantDocs.scroreTfIdfModel(path_raw=path)
    # relevantDocs.loadFromPath(path)
    corpus = Corpus(path=path)
    ese = ElasticsearchExporter(index=ConstantValues.ACL_CORPUS_INDEX, doc_type=ConstantValues.ACL_CORPUS_DOCTYPE)
    docIds = ese.getAllDocsByIndex()
    # print(len(docIds))
    docs = corpus.getHighReference(threshold=20, v=docIds)
    # print(len(docs))
    print(docs)
    selected_docs = getRandomDocs(listdocs=docs, MAXSIZE=100)
    ransel.selectFiles(path, "inputs/", selected_docs, method="copy")

if __name__ == '__main__':
    main()
