# T: Concept Graph
# Jonathan Gordon

import sys
import networkx as nx
import json
import uuid

# Parameters

WORDS_PER_CONCEPT = 100

###

class ConceptGraph:
    def __init__(self, fname=None):
        self.id = str(uuid.uuid4())
        self.provenance = 'TechKnAcq'
        self.type = '1.0'
        # We export lists of (concept) nodes and edges, but we internally
        # store everything as a NetworkX graph.
        self.g = nx.DiGraph()

        if fname:
            self.load(fname)


    def add_docs(self, corpus):
        """Add each document from the corpus as a node in the ConceptGraph
        and add edges for any citation information."""

        for doc in corpus:
            self.g.add_node(doc.id, type='document', authors=doc.authors,
                            title=doc.title, book=doc.book, year=doc.year,
                            url=doc.url, abstract=doc.get_abstract())
            for ref in doc.references:
                self.g.add_edge(doc.id, ref, type='cite')


    def add_concepts(self, model):
        """Add each topic from the topic model as a node in the
        ConceptGraph."""

        # Add a concept node for each topic in the model.
        for i, topic in enumerate(model.topics):
            concept_id = 'concept-' + str(i)
            self.g.add_node(concept_id, type='concept', words=[], mentions=0,
                            name=model.names[i])
            for word, weight in sorted(topic, key=lambda x: x[1], reverse=True):
                self.g.node[concept_id]['words'].append((word, weight))
                self.g.node[concept_id]['mentions'] += weight

        # Link the concept nodes to documents.
        for topic_id in range(len(model.topic_doc)):
            for base, percent in model.topic_doc[topic_id]:
                if percent == 0.0:
                    continue
                self.g.add_edge('concept-' + str(topic_id), base,
                                type='topic', weight=percent)


    def add_dependencies(self, edges):
        for t1 in edges:
            for t2 in edges[t1]:
                self.g.add_edge('concept-' + t1, 'concept-' + t2,
                                type='dependency', weight=edges[t1][t2])


    def docs(self):
        """Return a list of all document IDs in the concept graph."""
        return (n for n in self.g if
                self.g.node[n].get('type', '') == 'document')


    def topic_docs(self, topic_id):
        """Return a sorted list of (document_id, weight) pairs for the
        documents that are most relevant to the specified topic_id."""

        edges = []
        for (_, doc, weight) in self.g.edges([topic_id], data='weight'):
            if self.g.node[doc].get('type', '') == 'document':
                edges.append((doc, weight))
        return sorted(edges, key=lambda x: x[1], reverse=True)


    def topic_deps(self, topic_id):
        """Return a sorted list of (topic_id, weight) pairs for the
        topics that are most relevant to the specified topic_id."""

        edges = []
        for (_, t2, weight) in self.g.edges([topic_id], data='weight'):
            if self.g.edge[topic_id][t2]['type'] == 'dependency':
                edges.append((t2, weight))

        return sorted(edges, key=lambda x: x[1], reverse=True)


    def doc_cites(self, doc_id):
        """Return a list of the document IDs for the documents
        that are cited by the specified document."""

        edges = []
        for (_, d2) in self.g.edges([doc_id]):
            if self.g.edge[doc_id][d2]['type'] == 'cite':
                edges.append(d2)
        return edges


    def concepts(self):
        return (n for n in self.g if
                self.g.node[n].get('type', '') == 'concept')


    def load(self, fname):
        j = json.load(open(fname))

        try:
            self.id = j['id']
            self.provenance = j['provenance']
            self.type = j['type']

            for c in j['nodes']:
                self.g.add_node(c['id'], type='concept', words=[])
                self.g.node[c['id']]['name'] = c['name']
                self.g.node[c['id']]['mentions'] = c['mentionCount']
                for f in c['featureWeights']:
                    self.g.node[c['id']]['words'].append((f['feature'],
                                                          f['count']))
                self.g.node[c['id']]['words'].sort(key=lambda x: x[1],
                                                   reverse=True)

            for d in j['corpus']['docs']:
                self.g.add_node(d['id'], type='document',
                                authors=[x['fullName'] for x in d['authors']],
                                title=d['title'], book=d['book'],
                                year=d['year'], url=d['url'],
                                abstract=d['abstractText'])
                for cited in d['cites']:
                    self.g.add_edge(d['id'], cited, type='cite')

            for e in j['edges']:
                self.g.add_edge(e['source'], e['target'], type=e['type'],
                                weight=e['weight'])

            # XXX: Load document-concept edges

        except:
            sys.stderr.write('Error importing concept graph %s.\n' % (fname))
            sys.exit(1)


    def export(self, file='concept-graph.json'):
        """Export the concept graph as a JSON file."""

        j = {'id': self.id,
             'provenance': self.provenance,
             'type': self.type,
             'nodes': [],
             'edges': [],
             'corpus': {'id': str(uuid.uuid4()),
                        'name': '',
                        'description': '',
                        'docs': []}}

        # Add concept nodes and their (topic model) features.
        for c in self.concepts():
            j_concept = {'id': c,
                         'name': self.g.node[c]['name'],
                         'mentionCount': self.g.node[c]['mentions'],
                         'featureWeights': [],
                         'docWeights': []}

            for (word, weight) in self.g.node[c].get('words', []):
                j_concept['featureWeights'].append({'feature': word,
                                                    'count': int(weight)})

            for (doc, weight) in self.topic_docs(c):
                j_concept['docWeights'].append({'document': doc,
                                                'weight': weight})
            j['nodes'].append(j_concept)

        for doc_id in self.docs():
            j_doc = {'id': doc_id,
                     'url': self.g.node[doc_id]['url'],
                     'title': self.g.node[doc_id]['title'],
                     'authors': [{'id': x.lower().replace(' ', '_'),
                                  'fullName': x}
                                 for x in self.g.node[doc_id]['authors']],
                     'book': self.g.node[doc_id]['book'],
                     'year': self.g.node[doc_id]['year'],
                     'abstractText': self.g.node[doc_id]['abstract'],
                     'cites': self.doc_cites(doc_id),
                     'attributes': {}}
            j['corpus']['docs'].append(j_doc)

        for (t1, t2, data) in self.g.edges(data=True):
            if data.get('type', '') != 'dependency':
                continue
            j['edges'].append({'source': t1,
                               'target': t2,
                               'weight': data['weight'],
                               'type': 'dependency'})

        json.dump(j, open(file, 'w'), indent=2, sort_keys=True)
