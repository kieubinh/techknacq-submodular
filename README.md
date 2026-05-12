# TechKnAcq Submodular Reading Lists

This repository is a research prototype for generating academic reading lists from the ACL Anthology corpus. It extends the TechKnAcq toolkit with retrieval and submodular re-ranking experiments so a query paper can be mapped to a smaller, diverse, and relevant set of papers for a novice researcher to read.

The main ranking signals are:

- Elasticsearch/BM25 or TF-IDF relevance to the query paper.
- Concept-graph relevance from TechKnAcq topics.
- Author and citation influence signals.
- Submodular diversity penalties to reduce redundant recommendations.

## Repository Layout

- `RL_experiments.py` - main experiment runner for Elasticsearch/BM25, author, concept-graph, and submodular variants.
- `RL_CG_experiments.py` - older concept-graph experiment entry points.
- `config.example.yaml` - optional experiment configuration template for `RL_experiments.py`.
- `requirements.txt` - Python dependency list for the research scripts.
- `lib/elasticsearch/` - Elasticsearch import, export, retrieval, and submodular helpers.
- `lib/submodular/` - TF-IDF based relevant-document selection, submodular functions, and evaluation metrics.
- `lib/techknacq/` - corpus parsing, concept-graph, lexicon, and reading-list logic from TechKnAcq.
- `concept-graphs/` - generated concept graph JSON files.
- `inputs/`, `inputs-server/`, `sample-inputs/` - query/input document sets.
- `sample-score/`, `sample-bm25-score/` - sample document similarity scores.
- `results/`, `experiments/`, `log/` - historical experiment outputs and notes.
- `text-results/` - root-level text experiment summaries and incomplete-run notes.
- `reading-list`, `server`, `build-corpus`, `concept-graph` - TechKnAcq command-line utilities.

## Setup

The code was written as a Python research codebase and uses legacy Elasticsearch APIs such as `doc_type`, plus older NetworkX graph attributes such as `g.node` and `g.edge`. `requirements.txt` keeps those packages on compatible major versions.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m nltk.downloader punkt
```

On Windows, `pyenchant` may also require the Enchant native library to be installed separately.

## Input Format

Most experiment code expects ACL-style JSON documents with this shape:

```json
{
  "info": {
    "id": "acl-P12-1009",
    "title": "...",
    "year": "2012",
    "authors": ["..."]
  },
  "sections": [
    {"heading": "Abstract", "text": ["..."]}
  ],
  "references": ["acl-..."],
  "scores": {
    "acl-...": 0.42
  }
}
```

Experiment outputs are JSON files named like `<article-id>-output.json`:

```json
{
  "info": {
    "id": "acl-P12-1009",
    "count": 100
  },
  "output": ["acl-...", "acl-..."]
}
```

## Useful Commands

Run the concept-graph reading-list CLI:

```powershell
python reading-list concept-graphs/concept-graph-standard.json statistical parsing
```

Run the Flask reading-list server from this checkout:

```powershell
$env:PYTHONPATH = "lib"
python server concept-graphs/concept-graph-standard.json 9797
```

Run the main experiment driver after Elasticsearch and score files are available:

```powershell
python RL_experiments.py es
python RL_experiments.py es-au-sub
python RL_experiments.py --config config.example.yaml
```

Most historical experiment defaults still live near the top of `RL_experiments.py`, including `corpusInputPath`, `concept_graph`, output path, budget, and default submodular method. `config.example.yaml` can override those values without editing source code. Command-line methods take precedence over methods listed in the config file.

Evaluate result folders:

```powershell
python eval-experiments.py <output-folder> <answer-folder> <lambda>
```

Run a syntax-only check:

```powershell
python -m compileall -q lib baselines.py corpus-selection.py ES_importer.py eval-experiments.py RL_CG_experiments.py RL_experiments.py selection_corpus.py test-time.py training-calculate-similarity-scores.py util
```

## Algorithms

The code contains these submodular and baseline variants:

- `es` - Elasticsearch/BM25 ranking.
- `mlt` - more-like-this style ranking from precomputed score files.
- `es-sub` - Elasticsearch candidates followed by submodular selection.
- `es-au` - author/reference based recommendation.
- `es-au-sub` - query relevance plus author influence and submodular selection.
- `es-sub-cg` and `es-au-sub-cg` - concept graph candidates combined with submodular selection.
- `mmr_v1`, `mmr_v2`, `mmr_v3` - maximal marginal relevance variants.
- `mcr` - maximal concept relevance.
- `qfr_v1` - query-focused relevance.
- `qai_*` - query-author-influence variants.

## Relationship To NeuSub

This repository is the historical TechKnAcq/submodular experimentation code behind the citation-recommendation line of work that led to NeuSub. It contains the classical retrieval, author-signal, concept-graph, and submodular baselines used to generate and evaluate reading-list/citation recommendation outputs over ACL-style corpora.

The IEEE Access paper introduces the neural submodular approach: it combines deep neural representations, transformer models such as BERT and sentence-BERT, structural or multiclass hinge-loss training, and submodular inference for citation recommendation. This repository should be treated as the research artifact and baseline/prototype codebase rather than a polished standalone implementation of every neural model described in the paper.

## Citation

If you use this project, please cite:

```bibtex
@article{kieu2021neusub,
  author = {Kieu, B. T. and Unanue, I. J. and Pham, S. B. and Phan, H. X. and Piccardi, M.},
  title = {NeuSub: A Neural Submodular Approach for Citation Recommendation},
  journal = {IEEE Access},
  volume = {9},
  pages = {148459--148468},
  year = {2021},
  doi = {10.1109/ACCESS.2021.3120727},
  keywords = {Citation recommendation, deep neural networks, structural/multiclass hinge loss, submodular inference, transformer models, BERT, sentence-BERT}
}
```

## Development Notes

This is a historical research repository with many generated artifacts checked in. Keep refactors small and prefer preserving experiment defaults. Before changing ranking behavior, compile the code and run a known small sample so result JSON structure stays compatible with the existing evaluation scripts.
