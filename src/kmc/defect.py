import json
import os

import numpy as np


class DefectManager:
    def __init__(self, INITIAL_DEFECT_TYPE={}):

        self.INITIAL_DEFECT_TYPE = INITIAL_DEFECT_TYPE

    def read_defect_data(self, filename):

        raw_defect_data = np.loadtxt('data/' + filename,
                                     dtype=[('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'),
                                            ('y', 'f4'), ('z', 'f4')],
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

        filename = 'generate N = ' + str(N) + ' box = ' + BOX_SHAPE + ' L = ' + str(
            CHARACTERISTIC_LENGTH)
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
                print('%d %s %f %f %f' %
                      (i + 1, INITIAL_DEFECT_TYPE[flag], x * bound[1], y * bound[3], z * bound[5]),
                      file=f)
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
        for i, single_defect in enumerate(raw_defect_data):
            for j, defect_attr in enumerate(single_defect):
                if j == 1:
                    defect_data[i][j] = initial_defect_type[defect_attr]
                else:
                    defect_data[i][j] = defect_attr
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
            self.DEFECT = self.generate_defect_data(N, CHARACTERISTIC_LENGTH, BOX_SHAPE,
                                                    INITIAL_DEFECT_TYPE)
            return self.DEFECT
        if defect == 'read':
            self.DEFECT = self.read_defect_data(filename)
            return self.DEFECT


class DefectConfig:
    @staticmethod
    def write(path='./config', file_name='/defect_config.json', **kwargs):
        size = os.path.getsize(path + file_name)
        if size != 0:
            with open(path + file_name, 'r+') as f:
                defect_config = json.load(f)
                for i in kwargs:
                    if i not in defect_config.keys():
                        defect_config[i] = kwargs[i]
                    else:
                        for j in kwargs[i]:
                            if j not in defect_config[i].keys():
                                defect_config[i][j] = kwargs[i][j]
                            else:
                                if j == 'recombination':
                                    if isinstance(defect_config[i][j], dict) and isinstance(
                                            kwargs[i][j],
                                            dict) and defect_config[i][j] != kwargs[i][j]:
                                        defect_config[i][j] = [defect_config[i][j], kwargs[i][j]]
                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], dict) and (kwargs[i][j]
                                                                     not in defect_config[i][j]):
                                        defect_config[i][j].append(kwargs[i][j])
                                    if isinstance(defect_config[i][j], dict) and isinstance(
                                            kwargs[i][j], list) and (defect_config[i][j]
                                                                     not in kwargs[i][j]):
                                        defect_config[i][j] = kwargs[i][j].append(
                                            defect_config[i][j])
                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], list):
                                        temp = [
                                            kwelement for kwelement in kwargs[i][j]
                                            if kwelement not in defect_config[i][j]
                                        ]
                                        defect_config[i][j] += temp

                                else:
                                    defect_config[i][j] = kwargs[i][j]
                f.seek(0)
                f.truncate()
                json.dump(defect_config, f, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            with open(path + file_name, 'w+') as f:
                json.dump(kwargs, f, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def read(path='./config', file_name='/defect_config.json'):
        with open(path + file_name, 'r+') as f:
            defect_config = json.load(f)
        return defect_config


if __name__ == '__main__':
    DefectConfig.write(V={
        'migration': {
            'E': 5,
            'L': 1
        },
        'recombination': {
            'object': 'I',
            'E': 2
        }
    },
                       I={
                           'migration': {
                               'E': 0.5,
                               'L': 1
                           },
                           'recombination': [{
                               'object': 'I',
                               'E': 0.5
                           }, {
                               'object': 'V',
                               'E': 2
                           }]
                       })
    con = DefectConfig.read()
    print(con['I'])
