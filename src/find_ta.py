# coding=utf-8

"""Find the Translational Axis and project all MeSH terms onto it.
"""

__author__ = 'Qing Ke'
__email__ = 'keqing.echolife@gmail.com'


import simplejson as json
import numpy as np
import utils

from sklearn.metrics.pairwise import cosine_similarity


class TAFinder:
    """"""
    def __init__(self, in_path):
        self.duis, self.coordinates = utils.load_dui_coord(in_path)
        print(len(self.duis), self.coordinates.shape)
        self.dui2dname, self.dui2dtn = utils.load_dui_to_dname_dtn(2013)

    def find_translational_axis(self, out_path):
        """Find the Translational Axis"""
        axis = self.locate_human_centroid() - self.locate_animal_cell_centroid() # appliedness
        sim = cosine_similarity(self.coordinates, axis.reshape(1, -1)).flatten()
        dui_to_sim = dict(zip(self.duis, sim))
        with open(out_path, 'w') as fout:
            for dui, sim in sorted(dui_to_sim.items(), key=lambda x: x[1]):
                fout.write(json.dumps([dui, sim]) + '\n')

    def locate_human_centroid(self):
        """Locate the centroid of all human terms"""
        human_duis = utils.get_human_mesh(self.dui2dtn)
        indices = sorted(idx for idx, dui in enumerate(self.duis) if dui in human_duis)
        return np.mean(self.coordinates[indices, :], axis=0)

    def locate_animal_cell_centroid(self):
        """Locate the centroid of all animal and cell terms"""
        animal_duis = utils.get_animal_mesh(self.dui2dtn)
        cell_duis = utils.get_cell_mesh(self.dui2dtn)
        indices = sorted(idx for idx, dui in enumerate(self.duis) if dui in animal_duis or dui in cell_duis)
        return np.mean(self.coordinates[indices, :], axis=0)


if __name__ == '__main__':
    method = 'line'
    for yr in range(1980, 2014):
        print(yr)
        in_path = 'embed/mesh_cooccur_%d_%d.embed.%s' % (yr-4, yr, method)
        out_path = 'appliedness/mesh_appliedness_%s_%d_%d.json' % (method, yr-4, yr)
        finder = TAFinder(in_path)
        finder.find_translational_axis(out_path)
