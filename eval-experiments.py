from lib.submodular.evaluation import Evaluation


if __name__ == '__main__':

    eva = Evaluation()
    # eva.loadFiles("experiments/ground-truth-sample-v41/")
    eva.loadFiles("experiments/ground-truth-v41/")
    print("------------------F-score---------------------------------------------------------------------")
    eva.calAvgFscore()
    print("------------------MAP-------------------------------------------------------------------------")
    eva.calMAP()
    print("------------------MRR-------------------------------------------------------------------------")
    eva.calMRR()
    print("----------------------------------------------------------------------------------------------")
    print("avg_pre: "+str(eva.getAvgPrecision())+", avg_recall: "+str(eva.getAvgRecall())+" -> avg_fscore: "+str(eva.getAvgFscore()))
    print("MAP: " + str(eva.getMAP()))
    print("MAP2: " + str(eva.getMAP2()))
    print("MRR: " + str(eva.getMRR()))
    eva.getStatistics()
