# coding=utf-8

"""Utilities.
"""

__author__ = 'Qing Ke'
__email__ = 'keqing.echolife@gmail.com'


import numpy as np
import simplejson as json


def load_dui_to_dname_dtn(year):
    """Return mapping of descriptor unique ID (DUI) to descriptor name and tree numbers"""
    dui2dname, dui2dtn = {}, {}
    with open('../data/mesh/desc%d.json' % year) as fin:
        for line in fin:
            dui, dname, dtn, created = json.loads(line.strip())
            dui2dname[dui] = dname
            dui2dtn[dui] = dtn
    return dui2dname, dui2dtn

def is_target_dui(dui2dtn, dui):
    """Return whether DUI is a target one"""
    dtn = dui2dtn.get(dui, None)
    if dtn is None:
        return False
    for elem in dtn:
        if elem[0] in {'A', 'B', 'C', 'D', 'E', 'G', 'M', 'N'}:
            return True
    return False

def load_dui_coord(in_path):
    """Return DUI coordinates"""
    duis, coordinates = [], []
    with open(in_path) as fin:
        fin.readline()
        for line in fin:
            fields = line.strip().split()
            if fields[0] != '<unk>':
                duis.append(fields[0])
                coordinates.append([float(e) for e in fields[1:]])
    return duis, np.array(coordinates)

def load_mesh_appliedness(embed_method):
    """Return appliedness scores of DUIs"""
    return {yr: load_key_val_from_json('appliedness/mesh_appliedness_%s_%d_%d.json' % (embed_method, yr-4, yr)) for yr in range(1980, 2014)}

def load_key_val_from_json(in_path, key_index=0, val_index=1):
    """Return key-value mapping"""
    print(in_path)
    result = {}
    with open(in_path) as fin:
        for line in fin:
            fields = json.loads(line.strip())
            result[fields[key_index]] = fields[val_index]
    return result

def get_human_mesh(dui2dtn):
    """Return all human descriptors"""
    target_duis = ['D006801', 'D009272'] # Humans, Persons
    target_dtn = [dui2dtn[e][0] for e in target_duis]
    return get_dui_subtree(dui2dtn, target_dtn)

def get_animal_mesh(dui2dtn):
    """Return all animal descriptors"""
    target_duis = ['D056890'] # Eukaryota
    target_dtn = [dui2dtn[e][0] for e in target_duis]
    results = get_dui_subtree(dui2dtn, target_dtn)
    results.remove('D006801') # except left-node humans
    return results

def get_cell_mesh(dui2dtn):
    """Return all cell descriptors"""
    # Cells, Archaea, Bacteria, Viruses, Molecular Structure, Chemical Processes
    target_duis = ['D002477', 'D001105', 'D001419', 'D014780', 'D015394', 'D055599']
    target_dtn = [dui2dtn[e][0] for e in target_duis[:4]]
    target_dtn.append('G02.111.570') # D015394 has two tree numbers (G02.111.570 and G02.466), we need the first one
    target_dtn.append(dui2dtn[target_duis[5]][0])
    return get_dui_subtree(dui2dtn, target_dtn)

def get_dui_subtree(dui2dtn, target_dtn):
    """Return subtrees of given descriptor tree numbers"""
    results = set()
    for dui, dtn in dui2dtn.items():
        if dtn is not None:
            for tn in dtn:
                if any(tn.startswith(elem) for elem in target_dtn):
                    results.add(dui)
                    break
    return results
