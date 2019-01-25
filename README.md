# TechKnAcq-Submodular Tool (originated from TechKnAcq toolkit: https://github.com/ISI-TechKnAcq/techknacq-tk) 

# This tool supports novice researchers finding out a concept more quickly by recommending a reading list based on relevent concepts, diversity and redudancy of documents.

# Done
## calculate-scores.py: 
calculating similarity scores between documents and storing a tag "scores" in json files with document info (id, title, year, abstract...) and text info (sections).
Input: data/acl/*.json
Output: data/acl-score/*.json

## random-selection-corpus:
choosing a random (1/5) part of full corpus.
Input: data/acl/*.json
Output: data/acl-part/*.json

## submodular-experiments:
implement experiments for 4 submodular functions:
1. MMR - subMMR_MCR (method="mmr")
2. MRC - subMMR_MCR (method="mcr")
3. QFR - subQFR_UPR (method="qfr")
4. UPR - subQFR_UPR (method="upr")
Parameters:
  + path: with mmr and mrc -> concept-graph
  + method: 4 submodular functions
  + type-sim: type of information for calculating similarity score: "title", "abstract", "text"
  + Lambda: submodular = coverage - Lambda * redundancy

# To do
- Improving the running time: parallel? other submodular algorithm?
- 
