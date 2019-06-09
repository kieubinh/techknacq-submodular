from lib.submodular.evaluation import Evaluation

# lambda_test = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, -1, -2, -3]
# lambda_test = None
lambda_test = [-1, -2, -3, -4]

# -1 relevance, -2 authors, -3 influence


def eval_each_folder(output_folder=None, answer_folder=None, Lambda=-1):
    if (output_folder is None) or (answer_folder is None):
        return 0
    eva = Evaluation(hidden=True)
    eva.loadFiles(output_folder=output_folder, answer_folder=answer_folder)
    print("------------------F-score Lambda = %.2f --------------------" % Lambda)
    eva.calAvgFscore()
    print("------------------MAP-------------------------------------")
    eva.calMAP()
    print("------------------MRR-------------------------------------")
    eva.calMRR()
    print("----------------------------------------------------------")
    print("avg_pre: " + str(eva.getAvgPrecision()) + ", avg_recall: " + str(
        eva.getAvgRecall()) + " -> avg_fscore: " + str(eva.getAvgFscore()))
    print("MAP: " + str(eva.getMAP()))
    # print("MAP2: " + str(eva.getMAP2()))
    print("MRR: " + str(eva.getMRR()))
    eva.getStatistics()
    print("------------------END-------------------------------------")


def main():
    # eva.loadFiles("experiments/ground-truth-sample-v41/")
    eval_folder = "experiments/ground-truth-v41/"
    # output_folder_root = eval_folder + "acl-bm25-selection-12-1-qai_v2-100-1-1/"
    # output_folder_root = "results/laptop/19-06-09/acl-bm25-selection-12-1-qai_v2-100-1results\server\19-06-09-1/"
    output_folder_root = "results/server/19-06-09/acl-bm25-selection-12-1-qai_v12-100-1-1/"
    answer_folder = eval_folder + "selection-12-1/"

    if lambda_test is None:
        eval_each_folder(output_folder=output_folder_root, answer_folder=answer_folder)
        return 0
    elif len(lambda_test) == 0:
        lambda_test.append(-1)

    for Lambda in lambda_test:
        # print(Lambda)
        output_folder = output_folder_root + str(Lambda) + "/"
        eval_each_folder(output_folder=output_folder, answer_folder=answer_folder, Lambda=Lambda)


if __name__ == '__main__':
    main()