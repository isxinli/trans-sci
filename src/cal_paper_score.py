# encoding=utf-8

"""Calculate level score of papers.
"""

__author__ = 'Qing Ke'
__email__ = 'keqing.echolife@gmail.com'


import numpy as np
import simplejson as json
import utils


def calculate_score(yr2dui2sim, dui2dtn, out_path):
    """Average similarity"""
    fout = open(out_path, 'w')
    tot, poi = 0, 0
    for line in open('../data/medline_meta.json'):
        pmid, info = json.loads(line.strip())
        yr = int(info['year'][:4])
        if yr < 1980 or yr > 2013:
            continue
        tot += 1
        duis = [mesh['descriptor']['ui'] for mesh in info['mesh_heading_list']]
        scores = [yr2dui2sim[yr][dui] for dui in duis if utils.is_target_dui(dui2dtn, dui) and dui in yr2dui2sim[yr]]
        if len(scores) > 0 and 2 * len(scores) >= len(duis):
            out = [pmid, yr, duis, info['journal'], info['pub_type_list'], np.mean(scores)]
            poi += 1
            fout.write(json.dumps(out) + '\n')
    print('%d out of %d included' % (poi, tot))
    fout.close()


if __name__ == '__main__':
    method = 'line'
    _, dui2dtn = utils.load_dui_to_dname_dtn(2013)
    yr2dui2sim = utils.load_mesh_appliedness(method)
    out_path = 'results/paper_score_%s_1980_2013.json' % method
    calculate_score(yr2dui2sim, dui2dtn, out_path)
