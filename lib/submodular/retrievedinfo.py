import sys


class RetrievedInformation:
    def __init__(self, doc):
        self.query=""
        try:
            self.query=doc['info']['title']
        except Exception as e:
            print('Error reading JSON attribute: info->title')
            sys.exit(1)

    def getQuery(self):
        return self.query


