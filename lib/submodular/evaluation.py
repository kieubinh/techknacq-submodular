import os
import json
from lib.submodular.constantvalues import ConstantValues
import io
import sys

class Evaluation:
    def __init__(self):
        self.output = {}
        self.answer = {}
    def calFscore(self, output_ids=[], ground_ids=[]):
        if len(output_ids)==0:
            print("No output list!")
            return 0.0
        if len(ground_ids)==0:
            print("No ground true list!")
            return 1.0
        countTrue=0
        for id in output_ids:
            if id in ground_ids:
                countTrue+=1
        print("#correct: "+str(countTrue)+"/total output: "+str(len(output_ids))+"/total ground truth: "+str(len(ground_ids)))
        pre = 1.0*countTrue/len(ground_ids)
        recall = 1.0*countTrue/len(output_ids)
        if (countTrue==0):
            fscore=0.0
        else:
            fscore = 2.0*pre*recall/(pre+recall)
        return pre, recall, fscore


    #json file: {'output':[]} and {'answer':[]}
    def loadFiles(self, folderName=None):
        if folderName==None:
            print("No folder path")
        for root, dirs, files in os.walk(folderName, topdown=False):
            for nameFile in files:
                #must be json
                if "json" in nameFile:
                    # print(nameFile)
                    # file = open(root+"/"+nameFile, encoding="utf-8")
                    try:
                        data = json.load(io.open(root+"/"+nameFile, 'r', encoding='utf-8'))
                        nameId = data['info'].get('id','')
                        # print(nameId)
                        if len(nameId)>0:
                            # print(data[ConstantValues.ANSWER_KEY])
                            if ConstantValues.OUTPUT_KEY in data:
                                self.output[nameId]=data.get(ConstantValues.OUTPUT_KEY,[])
                            if ConstantValues.ANSWER_KEY in data:
                                self.answer[nameId]=data.get(ConstantValues.ANSWER_KEY,[])
                    except Exception as e:
                        print('Error reading JSON document:', nameFile, file=sys.stderr)
                        print(e, file=sys.stderr)
                        sys.exit(1)

    def calAvgFscore(self):
        sumPre = sumRecall = sumFscore = 0.0
        for name in self.output.keys():
            print(name)
            pre, recall, fscore = self.calFscore(self.output[name], self.answer[name])
            sumPre+=pre
            sumRecall+=recall
            sumFscore+=fscore

        self.avgPre = float(sumPre/len(self.answer.keys()))
        self.avgRecall = float(sumRecall/len(self.answer.keys()))
        self.avgFscore = float(sumFscore / len(self.answer.keys()))

    def getAvgPrecision(self):
        return self.avgPre

    def getAvgRecall(self):
        return self.avgRecall

    def getAvgFscore(self):
        return self.avgFscore
