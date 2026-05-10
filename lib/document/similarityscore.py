#Author: Binh Kieu Thanh
#Lib for similarity scores
#cosine similarity
#


import math
import re
from collections import Counter
#from lib.submodular.constantvalues import ConstantValues

WORD_RE = re.compile(r'\w+')


class SimilarityScore:

    def __init__(self, text1="", text2="", measure=0):
        self.text1 = text1 or ""
        self.text2 = text2 or ""
        self.measure = measure

    def getScore(self):
        if self.measure == 0:
            return self.cosineOf2Text(self.text1, self.text2)
        return 0.0

    @staticmethod
    def cosineOf2Text(text1, text2):
        vector1 = SimilarityScore.text_to_vector(text1)
        vector2 = SimilarityScore.text_to_vector(text2)

        return SimilarityScore.get_cosine(vector1, vector2)

    @staticmethod
    def text_to_vector(text):
        # if (text == "" or text == None):
        #     return 0
        #print(text)
        words = WORD_RE.findall(text or "")
        return Counter(words)

    @staticmethod
    def get_cosine(vec1, vec2):
        if isinstance(vec1, str):
            vec1 = SimilarityScore.text_to_vector(vec1)
        if isinstance(vec2, str):
            vec2 = SimilarityScore.text_to_vector(vec2)
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator
