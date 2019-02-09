from lib.submodular.evaluation import Evaluation


if __name__ == '__main__':

    eva = Evaluation()
    eva.loadFiles("experiments/ground-truth/")
    print(eva.calPre())