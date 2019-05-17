import sys


class RetrievedInformation:
    def __init__(self, doc):
        # print(doc['sections'][0])
        self.id = "acl"
        self.query = ""
        self.year = 0
        self.authors = []
        try:
            self.id = doc['info']['id']
            title = doc['info']['title']
            abstract = ""
            line_abstract = doc['sections'][0]['text']
            for line in line_abstract:
                abstract += line
            self.query = title + abstract
            self.year = int(doc['info']['year'])
            self.authors = doc['info']['authors']
        except Exception as e:
            print('Error reading JSON attribute')
            sys.exit(1)

    def getQuery(self):
        return self.query

    def getYear(self):
        return self.year

    def getAuthors(self):
        return self.authors

    def getId(self):
        return self.id
