import os

import numpy as np


class Defect:
    def __init__(self, INITIAL_DEFECT_TYPE={}):
        self.INITIAL_DEFECT_TYPE = INITIAL_DEFECT_TYPE

    def read_defect_data(self, filename):
        raw_defect_data = np.loadtxt('data/' + filename,
                                     dtype=[('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')],
                                     skiprows=1)
        defect_data = self.encode_defect(raw_defect_data)
        return defect_data

    def get_bound(self, BOX_SHAPE, CHARACTERISTIC_LENGTH):
        if BOX_SHAPE == 'cube':
            return (0, CHARACTERISTIC_LENGTH, 0, CHARACTERISTIC_LENGTH, 0, CHARACTERISTIC_LENGTH)
        if BOX_SHAPE == 'other':
            # TODO
            pass

    def generate_defect_data(self, N, CHARACTERISTIC_LENGTH, BOX_SHAPE, INITIAL_DEFECT_TYPE):

        filename = 'generate N = ' + str(N) + ' box = ' + BOX_SHAPE + ' L = ' + str(CHARACTERISTIC_LENGTH)
        datafiles = os.listdir('./data')
        index = 0
        indexed_filename = filename + '.txt'
        bound = self.get_bound(BOX_SHAPE, CHARACTERISTIC_LENGTH)

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
                print('%d %s %f %f %f' % (i + 1, INITIAL_DEFECT_TYPE[flag], x * bound[1], y * bound[3], z * bound[5]), file=f)
        return self.read_defect_data(indexed_filename)

    def encode_defect(self, raw_defect_data):
        initial_defect_type = {}
        defect_type_serial = 1

        for i in raw_defect_data:
            if i[1] not in initial_defect_type.keys():
                initial_defect_type[i[1]] = defect_type_serial
                defect_type_serial += 1
        self.INITIAL_DEFECT_TYPE = initial_defect_type

        defect_data = np.empty((raw_defect_data.shape[0], 5), dtype=np.float16)
        for i in range(len(defect_data)):
            for j in range(len(defect_data[i])):
                if j == 1:
                    defect_data[i][j] = initial_defect_type[raw_defect_data[i][j]]
                else:
                    defect_data[i][j] = raw_defect_data[i][j]
        print(defect_data, defect_data.shape)
        return defect_data

    def initialize_defect(self,
                          defect='generate',
                          filename=None,
                          N=1000,
                          CHARACTERISTIC_LENGTH=100,
                          BOX_SHAPE='cube',
                          INITIAL_DEFECT_TYPE=['I', 'V']):
        if defect == 'generate':
            return self.generate_defect_data(N, CHARACTERISTIC_LENGTH, BOX_SHAPE, INITIAL_DEFECT_TYPE)
        if defect == 'read':
            return self.read_defect_data(filename)


if __name__ == '__main__':
    d = Defect()
    data = d.generate_defect_data(100, 10)
