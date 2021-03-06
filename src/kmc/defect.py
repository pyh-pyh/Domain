import os

import numpy as np

from configs import SimulationConfig


class DefectManager:
    def __init__(self):

        self.DEFECT_TYPE_CONFIG = SimulationConfig.read_defect_type_config()
        self.BOX_SHAPE = SimulationConfig.read_simulation_box_config()['box_shape']
        self.BOX_LENGTH = SimulationConfig.read_simulation_box_config(
        )['box_length']
        self.initialize_defect()

    def initialize_defect(self,
                          defect='generate',
                          filename=None,
                          N=10000,
                          INITIAL_DEFECT_TYPE=['I', 'V']):

        if defect == 'generate':
            self.DEFECT = self.generate_defect_data(N, self.BOX_LENGTH, self.BOX_SHAPE,
                                                    INITIAL_DEFECT_TYPE)
        if defect == 'read':
            self.DEFECT = self.read_defect_data(filename)

    def read_defect_data(self, filename):

        raw_defect_data = np.loadtxt('data/' + filename,
                                     dtype=[('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'),
                                            ('y', 'f4'), ('z', 'f4')],
                                     skiprows=1)
        defect_data = self.encode_defect(raw_defect_data)
        return defect_data

    def get_bound(self, BOX_SHAPE, BOX_LENGTH):

        if BOX_SHAPE == 'cube':
            return (0, BOX_LENGTH, 0, BOX_LENGTH, 0, BOX_LENGTH)
        if BOX_SHAPE == 'other':
            # TODO other shape of simulation box
            pass

    def generate_defect_data(self, N, BOX_LENGTH, BOX_SHAPE, INITIAL_DEFECT_TYPE):

        filename = 'generate N = ' + str(N) + ' box = ' + BOX_SHAPE + ' L = ' + str(
            BOX_LENGTH)
        datafiles = os.listdir('./data')
        index = 0
        indexed_filename = filename + '.txt'
        bound = self.get_bound(BOX_SHAPE, BOX_LENGTH)

        while indexed_filename in datafiles:
            index += 1
            indexed_filename = filename + ' (' + str(index) + ').txt'

        with open('data/' + indexed_filename, 'a') as f:
            print(N, file=f)
            for i in range(N):
                flag = np.random.randint(len(INITIAL_DEFECT_TYPE))
                x = np.random.random_sample()
                y = np.random.random_sample()
                z = np.random.random_sample()
                print('%d %s %f %f %f' %
                      (i + 1, INITIAL_DEFECT_TYPE[flag], x * bound[1], y * bound[3], z * bound[5]),
                      file=f)
        return self.read_defect_data(indexed_filename)

    def encode_defect(self, raw_defect_data):

        defect_data = np.empty((raw_defect_data.shape[0], 5), dtype=np.float64)
        for i, single_defect in enumerate(raw_defect_data):
            for j, defect_attr in enumerate(single_defect):
                if j == 1:
                    defect_data[i][j] = self.DEFECT_TYPE_CONFIG[defect_attr]
                else:
                    defect_data[i][j] = defect_attr
        return defect_data


if __name__ == '__main__':
    d = DefectManager()
    print(d.DEFECT)
