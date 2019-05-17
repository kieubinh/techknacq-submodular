from lib.submodular.evaluation import Evaluation


if __name__ == '__main__':

    eva = Evaluation()
    eva.loadFiles("experiments/ground-truth-v35/")
    eva.calAvgFscore()
    print("--------------------------------------------------------------------------------------------------")
    eva.calMAP()
    print("avg_pre: "+str(eva.getAvgPrecision())+", avg_recall: "+str(eva.getAvgRecall())+" -> avg_fscore: "+str(eva.getAvgFscore()))
    print("map: "+str(eva.getMAP()))
    eva.getStatistics()
