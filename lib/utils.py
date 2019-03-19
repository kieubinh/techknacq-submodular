#author: Kieu Thanh Binh
#provide general functions

import math
import re
from collections import Counter

class Utils:
    def text_to_vector(text):
        WORD = re.compile(r'\w+')
        words = WORD.findall(text)
        return Counter(words)

    def get_cosine(vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator