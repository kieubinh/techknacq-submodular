import json
import io
import sys
from lib.constantvalues import ConstantValues


class SimilairtyScores:

    def __init__(self, fid, v=None):
        # print(fid)
        # print(v)
        self.id = fid
        self.score = None
        j = {'score': []}
        try:
            # print(fid)
            fname = ConstantValues.ACL_SCORES + "/" + fid + ".json"
            j = json.load(io.open(fname, 'r', encoding='utf-8'))
        except Exception as e:
            # print('Error reading JSON document:', fid, file=sys.stderr)
            print(e, file=sys.stderr)
            sys.exit(1)

        jscore = j.get('score', {})
        # doc_score = {}
        # sum_score = 0.0
        # for doc_id in v:
        #     if doc_id in jscore:
        #         doc_score[doc_id] = jscore[doc_id]
        #         sum_score += doc_score[doc_id]
        # doc_score[ConstantValues.OneVsRest] = sum_score
        self.score = jscore


