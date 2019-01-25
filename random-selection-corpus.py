
import glob
import random
import shutil
import os

# from pathlib import Path


def move(path_input="data/acl-score/", path_output="data/acl-score-part/", maxRange=2):
    for root, dirs, files in os.walk(path_input, topdown=False):
        print(root)
        for name in files:
            # print(name)
            #get random 1/5
            if random.randrange(maxRange)==0:
               shutil.move(path_input+name, path_output+name)


import sys

def main(path_input="data/acl-score/", path_output="data/acl-score-part/", oneOf=2):
    if len(sys.argv)>2:
        path_input = sys.argv[1]
        path_output = sys.argv[2]

    if len(sys.argv)>3:
        oneOf = int(sys.argv[3])

    print(path_input+" - "+path_output+" "+str(oneOf))
    move(path_input, path_output, oneOf)

if __name__ == '__main__':
    main()