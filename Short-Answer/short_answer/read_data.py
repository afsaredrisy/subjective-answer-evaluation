import os, csv

def read_data(filename):
    testdata = []
    scores = []
    BASE = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE, "train.tsv")) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter="\t")
        for line in tsvreader:
            if line[1] != "5":
                break
            testdata.append(str(line[4]))
            scores.extend(line[2])
    return (testdata, scores)