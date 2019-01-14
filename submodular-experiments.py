

import click
from lib.techknacq.conceptgraph import ConceptGraph
from lib.techknacq.readinglist import ReadingList
from lib.submodular.submodular import Submodular
from lib.submodular.constantvalues import ConstantValues

def subMMR(concept_graph, query):
    cg = ConceptGraph(click.format_filename(concept_graph))
    learner_model = {}
    for c in cg.concepts():
        learner_model[c] = ConstantValues.BEGINNER
    r = ReadingList(cg, query, learner_model)
    #print reading list
    #r.print()

    #summarise the reading list

    #convert r into list of papers
    r.convert2List()
    readinglist = r.getReadinglist()
    #before summarization
    print("Before Submodular: ")
    print(len(readinglist))
    for doc in readinglist:
        print(doc['id']+" - "+str(doc))
    #Lambda = 0 -> no penalty
    submodular = Submodular(readinglist)
    print("Lambda = 0 -> No penalty")
    Lambda = 0.0
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])

    #Lambda = 0.5 -> less penalty
    print("Lambda = 0.1")
    Lambda = 0.1
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])
    #Lambda = 1.0 -> same degree penalty
    print("Lambda = 0.3")
    Lambda = 0.3
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])
    #Lambda = 2.0 -> double degree penalty
    print("Lambda = 0.6")
    Lambda = 0.6
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])
    #Lambda = 3.0 -> as paper
    print("Lambda = 1.0")
    Lambda = 1.0
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])

    # Lambda = 2.0 -> as paper
    print("Lambda = 2.0")
    Lambda = 2.0
    summarizedlist = submodular.getSubmodular(Lambda=Lambda, method="mmr")
    print(len(summarizedlist))
    for doc in summarizedlist:
        print(doc['id'])


@click.command()
@click.argument('concept_graph', type=click.Path(exists=True))
@click.argument('query', nargs=-1)
def main(concept_graph, query):
    subMMR(concept_graph, query)

if __name__ == '__main__':

    main()