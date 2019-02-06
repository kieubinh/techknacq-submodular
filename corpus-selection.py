

from lib.submodular.relevantdocuments import RelevantDocuments
from lib.techknacq.corpus import Corpus

import click
@click.command()
@click.argument('path', type=click.Path(exists=True))
# @click.argument('query', nargs=-1)
def main(path="data/acl/"):
    # relevantDocs = RelevantDocuments()
    # relevantDocs.scroreTfIdfModel(path_raw=path)
    # relevantDocs.loadFromPath(path)
    corpus = Corpus(path=path)
    docs = corpus.getHighReference(threshold=30)
    print(len(docs))
    print(docs)

if __name__ == '__main__':
    main()