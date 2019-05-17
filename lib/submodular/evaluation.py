import os
import json
from lib.constantvalues import ConstantValues
import io
import sys


class Evaluation:
    def __init__(self):
        self.output = {}
        self.answer = {}
        self.sumCorrect = 0
        return None

    def calFscore(self, output_ids=[], ground_ids=[]):
        # print(len(output_ids))
        if len(output_ids) == 0:
            print("No output list!")
            print("#correct: 0/total output: " + str(len(output_ids)) + "/total ground truth: " + str(len(ground_ids)))

            return 0.0, 0.0, 0.0
        if len(ground_ids) == 0:
            print("No ground true list!")
            return 1.0, 1.0, 1.0
        ccorrect = 0
        for id in output_ids:
            if id in ground_ids:
                ccorrect += 1
        print("#correct: " + str(ccorrect) + "/total output: " + str(len(output_ids)) + "/total ground truth: " + str(
            len(ground_ids)))
        self.sumCorrect += ccorrect
        pre = 1.0 * ccorrect / len(output_ids)
        recall = 1.0 * ccorrect / len(ground_ids)
        if ccorrect == 0:
            fscore = 0.0
        else:
            fscore = 2.0 * pre * recall / (pre + recall)
        return pre, recall, fscore

    # json file: {'output':[]} and {'answer':[]}
    def loadFiles(self, folderName=None):
        if folderName == None:
            print("No folder path")
        for root, dirs, files in os.walk(folderName, topdown=False):
            for nameFile in files:
                # must be json
                if "json" in nameFile:
                    # print(nameFile)
                    # file = open(root+"/"+nameFile, encoding="utf-8")
                    try:
                        data = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                        nameId = data['info'].get('id', '')
                        # print(nameId)
                        if len(nameId) > 0:
                            # print(data[ConstantValues.ANSWER_KEY])
                            if ConstantValues.OUTPUT_KEY in data:
                                self.output[nameId] = data.get(ConstantValues.OUTPUT_KEY, [])
                            if ConstantValues.ANSWER_KEY in data:
                                self.answer[nameId] = data.get(ConstantValues.ANSWER_KEY, [])
                    except Exception as e:
                        print('Error reading JSON document:', nameFile, file=sys.stderr)
                        print(e, file=sys.stderr)
                        sys.exit(1)

    def calAvgFscore(self):
        sumPre = sumRecall = sumFscore = 0.0
        for name in self.output.keys():
            print(name)
            pre, recall, fscore = self.calFscore(self.output[name], self.answer[name])
            sumPre += pre
            sumRecall += recall
            sumFscore += fscore

        self.avgPre = float(sumPre / len(self.output))
        self.avgRecall = float(sumRecall / len(self.output))
        self.avgFscore = float(sumFscore / len(self.output))

    def getAvgPrecision(self):
        return self.avgPre

    def getAvgRecall(self):
        return self.avgRecall

    def getAvgFscore(self):
        return self.avgFscore

    def getStatistics(self):
        sumout = 0
        sumans = 0
        for name in self.output.keys():
            sumout += len(self.output[name])
            sumans += len(self.answer[name])

        print("# output: %i, #answer: %i, total refs of answer: %i, #correct: %i" % (len(self.output), len(self.answer), sumans, self.sumCorrect))

        print("# average output: " + str(1.0 * sumout / len(self.output)))
        print("# average answer: " + str(1.0 * sumans / len(self.output)))

    # Calculating MAP score
    def calPrec(self, ground_ids=[], output_ids=[]):
        count = 0
        for id in output_ids:
            if id in ground_ids:
                count += 1
        return count / len(output_ids)

    def calAvgPrec(self, output_ids=[], ground_ids=[]):
        # print(len(output_ids))
        if len(output_ids) == 0:
            print("No output list!")
            print("#correct: 0/total output: " + str(len(output_ids)) + "/total ground truth: " + str(len(ground_ids)))
            return 0.0
        prec = 0.0
        for index in range(0, len(output_ids)):
            if output_ids[index] in ground_ids:
                prec += self.calPrec(ground_ids, output_ids[0:index+1])

        return prec / len(ground_ids)

    def calMAP(self):
        map_score = 0.0
        for name in self.output.keys():

            avg_prec = self.calAvgPrec(self.output[name], self.answer[name])
            print(name+" : "+str(avg_prec))
            map_score += avg_prec
        self.mapScore = map_score / len(self.output)

    def getMAP(self):
        return self.mapScore
