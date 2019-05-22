from lib.constantvalues import ConstantValues


class ArticleInformation:
    def __init__(self, doc):
        # print(doc['sections'][0])
        self.doc = doc
        self.id = "acl"
        self.query = None
        self.year = 0
        self.authors = []
        self.title = None
        self.abstract = None
        try:
            self.id = doc['info']['id']
            self.year = int(doc['info']['year'])
            self.authors = doc['info']['authors']
        except Exception as e:
            print('Error reading JSON attribute - id, year, authors')
            # print(doc)
            return

    def getQuery(self):
        return self.getTitleAbs()

    def getTitle(self):
        if self.title is not None:
            return self.title
        try:
            self.title = self.doc['info']['title']
        except Exception as e:
            print('Error reading JSON attribute - title')
            # print(doc)
            return None
        return self.title

    def getAbstract(self):
        if self.abstract is not None:
            return self.abstract
        self.abstract = ""
        try:
            abstract = ""
            line_abstract = self.doc['sections'][0]['text']
            for line in line_abstract:
                if len(line) + len(abstract) >= ConstantValues.MAX_LENGTH_QUERY:
                    break
                abstract += line

            self.abstract = abstract
        except Exception as e:
            print('Error reading JSON attribute - abstract')
            # print(doc)

        return self.abstract

    def getTitleAbs(self):
        return self.getTitle() + "\n" + self.getAbstract()

    def get5TitleAbs(self):
        return self.getTitle() + "\n" + self.getAbstract() + "\n" \
               + self.getTitle() + "\n" + self.getTitle() + "\n" + self.getTitle() + "\n" + self.getTitle()

    def getYear(self):
        return self.year

    def getAuthors(self):
        return self.authors

    def getId(self):
        return self.id
