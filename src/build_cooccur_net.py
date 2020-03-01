# coding=utf-8

"""Build weighted co-occurrence networks.
"""

__author__ = 'Qing Ke'
__email__ = 'keqing.echolife@gmail.com'


import networkx as nx
import os
import simplejson as json
import utils

from collections import Counter
from ctypes import Structure
from itertools import combinations


class EdgeStruct(Structure):
    _fields_ = [('s', c_int), ('t', c_int), ('w', c_double)]

def load_data(in_path='../data/medline_meta.json'):
    """Return list of papers; each is a tuple of PubMed ID, publication year, and a list of MeSH descriptors"""
    result = []
    with open(in_path) as fin:
        for line in fin:
            pmid, info = json.loads(line.strip())
            year = int(info['year'][:4])
            duis = [mesh['descriptor']['ui'] for mesh in info['mesh_heading_list']]
            result.append((pmid, year, duis))
    return result

def build_year_range(papers, year_range, out_format, dui2dtn):
    """Construct weighted co-occurrence network for the given period"""
    dui_freq = Counter()
    network = nx.Graph()
    bgn_yr, end_yr = year_range
    for pmid, yr, duis in papers:
        if yr < bgn_yr or yr > end_yr:
            continue
        target_duis = [d for d in duis if utils.is_target_dui(dui2dtn, d)]
        dui_freq.update(target_duis)
        [network.add_node(d) for d in target_duis if d not in network]
        for d1, d2 in combinations(target_duis, 2):
            if d2 in network[d1]:
                network[d1][d2]['weight'] += 1
            else:
                network.add_edge(d1, d2, weight=1)
    if not os.path.exists('network/'):
        os.mkdir('network/')
    # both methods output an edge twice
    if out_format == 'LINE': # used by LINE
        out_path = 'network/mesh_cooccur_%d_%d.tsv' % (bgn_yr, end_yr)
        with open(out_path, 'w') as fout:
            for u, v, d in network.edges(data=True):
                fout.write('\t'.join([u, v, str(d['weight'])]) + '\n')
                fout.write('\t'.join([v, u, str(d['weight'])]) + '\n')
    elif out_format == 'GloVe': # used by GloVe
        dui_to_idx = {}
        vocab_path = 'network/mesh_vocab_%d_%d.txt' % (bgn_yr, end_yr)
        with open(vocab_path, 'w') as fout:
            for idx, (dui, freq) in enumerate(dui_freq.most_common(), 1):
                dui_to_idx[dui] = idx
                fout.write(dui + ' ' + str(freq) + '\n')
        out_path = 'network/mesh_cooccur_%d_%d.bin' % (bgn_yr, end_yr)
        with open(out_path, 'wb') as fout:
            for u, v, d in network.edges(data=True):
                fout.write( EdgeStruct(dui_to_idx[u], dui_to_idx[v], d['weight']) )
                fout.write( EdgeStruct(dui_to_idx[v], dui_to_idx[u], d['weight']) )

def build_all(papers, dui2dtn, out_format='LINE'):
    """Sliding window"""
    if out_format not in {'LINE', 'GloVe'}:
        return
    for yr in range(1980, 2014):
        print(yr)
        build_year_range(papers, (yr-4,yr), out_format, dui2dtn)


if __name__ == '__main__':
    dui2dname, dui2dtn = utils.load_dui_to_dname_dtn(2013)
    papers = load_data()
    build_all(papers, dui2dtn)
