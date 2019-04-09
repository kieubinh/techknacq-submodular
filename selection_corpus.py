# import glob
import random
import shutil
import os
import io
import json
import sys
from pathlib import Path
from lib.constantvalues import ConstantValues

answer = []
# from pathlib import Path
selectList = [
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
    "acl-C08-2022",
    "acl-C10-2118",
    "acl-D07-1010",
    "acl-D08-1020",
    "acl-D09-1036",
    "acl-D11-1027",
    "acl-H01-1035",
    "acl-H05-1108",
    "acl-I08-7009",
    "acl-L08-1093",
    "acl-P03-1056",
    "acl-P06-2057",
    "acl-P09-1042",
    "acl-P09-1077",
    "acl-P09-2004",
    "acl-P11-1061",
    "acl-P11-1100",
    "acl-P11-2052",
    "acl-P11-2111",
    "acl-P12-1008",
    "acl-P97-1011",
    "acl-P97-1013",
    "acl-W04-1101",
    "acl-W09-3029",
    "acl-W11-2022",
    "acl-D09-1123",
    "acl-D10-1027",
    "acl-H05-1066",
    "acl-N03-1017",
    "acl-N04-1035",
    "acl-N07-1051",
    "acl-N12-1015",
    "acl-P03-1021",
    "acl-P04-1015",
    "acl-P05-1034",
    "acl-P06-1077",
    "acl-P06-1121",
    "acl-P08-1023",
    "acl-P08-1066",
    "acl-P09-1063",
    "acl-P10-1110",
    "acl-P10-1145",
    "acl-P11-1063",
    "acl-W04-0308",
    "acl-W04-3250",
    "acl-D07-1090",
    "acl-D08-1022",
    "acl-D08-1060",
    "acl-D08-1076",
    "acl-D10-1027",
    "acl-D11-1020",
    "acl-D11-1127",
    "acl-D12-1109",
    "acl-E09-1044",
    "acl-J07-2003",
    "acl-J10-2004",
    "acl-J10-3008",
    "acl-N07-1051",
    "acl-N13-1060",
    "acl-P02-1040",
    "acl-P03-2041",
    "acl-P05-1033",
    "acl-P06-1077",
    "acl-P06-1121",
    "acl-P07-1019",
    "acl-P08-1023",
    "acl-P08-1064",
    "acl-P08-1114",
    "acl-P09-1063",
    "acl-P09-1065",
    "acl-P10-1146",
    "acl-P12-3004",
    "acl-W06-1606",
    "acl-W06-3119",
    "acl-W10-1761",
    "acl-C04-1200",
    "acl-C10-2011",
    "acl-D07-1115",
    "acl-D08-1108",
    "acl-D09-1063",
    "acl-D09-1094",
    "acl-D11-1063",
    "acl-E09-1077",
    "acl-E99-1042",
    "acl-H05-1044",
    "acl-N07-1037",
    "acl-N10-1119",
    "acl-P02-1053",
    "acl-P10-1041",
    "acl-P13-1025",
    "acl-P13-1094",
    "acl-P13-2090",
    "acl-P97-1023",
    "acl-W06-1642",
    "acl-W11-0711"
]


def randomMove(path_input="data/acl-score/", path_output="data/acl-score-part/", maxRange=2):
    for root, dirs, files in os.walk(path_input, topdown=False):
        print(root)
        for name in files:
            # print(name)
            # get random 1/5
            if random.randrange(maxRange) == 0:
                shutil.move(path_input + name, path_output + name)


def selectFiles(path_input="data/acl-score/", path_output="data/acl-score-select/", seList=selectList, method="move"):
    jsonList = []
    for name in seList:
        jsonList.append(name + ".json")

    # print(jsonList)
    for root, dirs, files in os.walk(path_input, topdown=False):
        print(root)
        for name in files:
            # print(name)
            # get random 1/5
            if name in jsonList:
                if method == "move":
                    shutil.move(path_input + name, path_output + name)
                elif method == "copy":
                    shutil.copy(path_input + name, path_output + name)


def main(path_input="data/acl/", path_output="data/acl-select/", oneOf=5):
    if len(sys.argv) > 2:
        path_input = sys.argv[1]
        path_output = sys.argv[2]

    if len(sys.argv) > 3:
        oneOf = int(sys.argv[3])

    print(path_input + " - " + path_output + " " + str(oneOf))
    # randomMove(path_input, path_output, oneOf)
    selectFiles(path_input, path_output, selectList, method="move")


def makeCorpus(corpusPath="data/acl/", selectPath="data/acl-select/", inputPath="sample-high/"):
    for root, dirs, files in os.walk(inputPath, topdown=False):
        for nameFile in files:
            # must be json
            if "json" in nameFile:
                # print(nameFile)
                # file = open(root+"/"+nameFile, encoding="utf-8")
                try:
                    data = json.load(io.open(root + "/" + nameFile, 'r', encoding='utf-8'))
                    nameId = data['info'].get('id', '')
                    print(nameId)
                    if len(nameId) > 0:
                        # print(data[ConstantValues.ANSWER_KEY])
                        if ConstantValues.ANSWER_KEY in data:
                            refList = data.get(ConstantValues.ANSWER_KEY, [])
                            for ref in refList:
                                if ref not in answer:
                                    answer.append(ref)
                except Exception as e:
                    print('Error reading JSON document:', nameFile, file=sys.stderr)
                    print(e, file=sys.stderr)
                    sys.exit(1)
    print("length of answer list: " + str(len(answer)))
    selectFiles(corpusPath, selectPath, answer, method="copy")


def makeInputsByYears(corpusPath="data/acl/", inputPath="inputs/years/"):
    for root, dirs, files in os.walk(corpusPath, topdown=False):
        for name_file in files:
            # must be json
            if "json" in name_file:
                print(name_file)
                file_path = root+"/"+name_file
                new_file_folder = inputPath+name_file[5:7]
                path_folder = Path(new_file_folder)
                if not path_folder.is_dir():
                    os.mkdir(new_file_folder)
                shutil.copy(file_path, new_file_folder+"/"+name_file)

if __name__ == '__main__':
    # makeCorpus("data/acl/", "data/acl-select/", "sample-high/")
    makeInputsByYears(corpusPath="../data/acl/", inputPath="inputs/years/")