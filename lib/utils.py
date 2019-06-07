#author: Kieu Thanh Binh
#provide general functions

import math
import re
from collections import Counter
import io
import json
from pathlib import Path
import collections


from lib.constantvalues import ConstantValues

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

    def getSimDocFromCorpus(doc_id=None, score_folder=ConstantValues.ACL_SCORES):
        if doc_id is None:
            return None
        file_name = score_folder + "/" + doc_id + ".json"
        file_path = Path(file_name)
        if file_path.exists():
            # print(file_name)
            json_data = json.load(io.open(file_name, 'r', encoding='utf-8'))
            file_doc_id = json_data['info']['id']
            if file_doc_id == doc_id:
                return json_data['score']
            else:
                # if not same id
                return None
        return None

    def getYearFromId(doc_id=None):
        if doc_id is None:
            return 0
        str_year = doc_id[5:7]
        num_year = int(str_year)
        if num_year > 50:
            return 1900+num_year
        else:
            return 2000+num_year

    def get_top_dict(dict={}, budget=100):
        # return: sort and return top budget
        top_dict = {}
		index = 0
		for k, v in sorted(dict.items(), key=lambda x: x[1], reverse=True):
			top_dict[k] = v
			index += 1
			if index >= budget:
                return top_dict

        return top_dict
             
