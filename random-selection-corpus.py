
import glob
import random
import shutil
import os

# from pathlib import Path

class RandomSelection:
    def __init__(self, path="data/acl"):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                #get random 1/5
                if random.randrange(6)==0:
                    shutil.move(path+"/"+name, path+"/acl-part/"+name)



RandomSelection()

