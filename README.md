## [Identifying translational science through embeddings of controlled vocabularies](http://dx.doi.org/10.1093/jamia/ocy177)

Workflow:

1. `build_cooccur_net.py`
1. Run [`LINE`](https://github.com/tangjianpku/LINE) or [`GloVe`](https://github.com/stanfordnlp/GloVe) to get the embeddings of MeSH terms;
1. `find_ta.py`
1. `cal_paper_score.py`
