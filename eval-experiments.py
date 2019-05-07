from lib.submodular.evaluation import Evaluation


if __name__ == '__main__':

    eva = Evaluation()
    eva.loadFiles("experiments/ground-truth-v35/")
    eva.calAvgFscore()
    print("avg_pre: "+str(eva.getAvgPrecision())+", avg_recall: "+str(eva.getAvgRecall())+" -> avg_fscore: "+str(eva.getAvgFscore()))
    eva.getStatistics()
