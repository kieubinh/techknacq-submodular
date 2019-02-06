
import glob
import random
import shutil
import os

# from pathlib import Path
selectList=[
    "acl-C10-2158",
    "acl-D08-1105",
    "acl-J05-1004",
    "acl-J08-2004",
    "acl-J08-2006",
    "acl-J93-2004",
    "acl-L08-1093",
    "acl-L08-1461",
    "acl-N01-1016",
    "acl-N07-1051",
    "acl-N09-1037",
    "acl-N13-1071",
    "acl-P02-1014",
    "acl-P05-1022",
    "acl-P05-1045",
    "acl-P06-1005",
    "acl-P08-1091",
    "acl-P10-4014",
    "acl-P11-2037",
    "acl-S10-1001",
    "acl-W00-1322",
    "acl-W01-0521",
    "acl-W04-1602",
    "acl-W05-0620",
    "acl-W06-0609",
    "acl-W10-1836",
    "acl-W11-1901",
    "acl-W11-1905",
    "acl-W12-4501",
    "acl-W12-4503",
    "acl-L08-1384",
    "acl-N04-1013",
    "acl-N06-1058",
    "acl-P05-1022",
    "acl-P10-2016",
    "acl-P11-1022",
    "acl-P12-3024",
    "acl-P13-1004",
    "acl-P13-1135",
    "acl-P13-2135",
    "acl-P13-4014",
    "acl-S13-1034",
    "acl-W02-1001",
    "acl-W06-3114",
    "acl-W07-0718",
    "acl-W08-0309",
    "acl-W09-0401",
    "acl-W09-0441",
    "acl-W10-1703",
    "acl-W10-1751",
    "acl-W11-2103",
    "acl-W11-2104",
    "acl-W12-3102",
    "acl-W12-3113",
    "acl-W12-3118",
    "acl-W13-2202",
    "acl-W13-2204",
    "acl-W13-2205",
    "acl-W13-2206",
    "acl-W13-2207",
    "acl-W13-2208",
    "acl-W13-2209",
    "acl-W13-2210",
    "acl-W13-2211",
    "acl-W13-2212",
    "acl-W13-2213",
    "acl-W13-2214",
    "acl-W13-2215",
    "acl-W13-2216",
    "acl-W13-2217",
    "acl-W13-2218",
    "acl-W13-2219",
    "acl-W13-2220",
    "acl-W13-2221",
    "acl-W13-2222",
    "acl-W13-2223",
    "acl-W13-2224",
    "acl-W13-2225",
    "acl-W13-2226",
    "acl-W13-2227",
    "acl-W13-2228",
    "acl-W13-2229",
    "acl-W13-2230",
    "acl-W13-2240",
    "acl-W13-2241",
    "acl-W13-2242",
    "acl-W13-2243",
    "acl-W13-2244",
    "acl-W13-2246",
    "acl-W13-2247",
    "acl-W13-2248",
    "acl-W13-2249",
    "acl-W13-2250",
    "acl-W13-2253",
    "acl-W13-2255",
    "acl-C10-1063",
    "acl-C10-1064",
    "acl-D07-1096",
    "acl-D09-1086",
    "acl-D10-1030",
    "acl-D10-1120",
    "acl-D11-1006",
    "acl-D11-1014",
    "acl-D11-1110",
    "acl-D12-1001",
    "acl-D12-1125",
    "acl-D13-1141",
    "acl-H05-1066",
    "acl-N01-1026",
    "acl-N12-1052",
    "acl-N13-1006",
    "acl-N13-1126",
    "acl-P04-1013",
    "acl-P05-1012",
    "acl-P07-1080",
    "acl-P09-1007",
    "acl-P09-1042",
    "acl-P10-1040",
    "acl-P10-1156",
    "acl-P11-1061",
    "acl-P12-1066",
    "acl-P12-1068",
    "acl-P12-1073",
    "acl-P12-2010",
    "acl-P13-1105",
    "acl-Q14-1005",
    "acl-W06-2920",
    "acl-W10-2906",
  ]

def randomMove(path_input="data/acl-score/", path_output="data/acl-score-part/", maxRange=2):
    for root, dirs, files in os.walk(path_input, topdown=False):
        print(root)
        for name in files:
            # print(name)
            #get random 1/5
            if random.randrange(maxRange)==0:
               shutil.move(path_input+name, path_output+name)

def selectMove(path_input="data/acl-score/", path_output="data/acl-score-select/", seList=selectList):
    jsonList = []
    for name in seList:
        jsonList.append(name+".json")

    # print(jsonList)
    for root, dirs, files in os.walk(path_input, topdown=False):
        print(root)
        for name in files:
            # print(name)
            #get random 1/5
            if (name in jsonList):
               shutil.move(path_input+name, path_output+name)

import sys

def main(path_input="data/acl-score/", path_output="data/acl-score-select/", oneOf=2):
    if len(sys.argv)>2:
        path_input = sys.argv[1]
        path_output = sys.argv[2]

    if len(sys.argv)>3:
        oneOf = int(sys.argv[3])

    print(path_input+" - "+path_output+" "+str(oneOf))
    # randomMove(path_input, path_output, oneOf)
    selectMove(path_input, path_output, selectList)


if __name__ == '__main__':
    main()