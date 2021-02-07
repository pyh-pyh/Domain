import os

import numpy as np


class Defect:
    def read_defect_data(self, filename):
        raw_defect_data = np.loadtxt('data/' + filename, 
                                     dtype = [('ID', 'i4'), 
                                              ('type', np.str, 10), 
                                              ('x', 'f4'), 
                                              ('y', 'f4'), 
                                              ('z', 'f4')], 
                                     skiprows = 1)
        defect_data = self.encode_defect(raw_defect_data)
        return defect_data

    def generate_defect_data(self, 
                             N, 
                             bound, 
                             BOX_SHAPE, 
                             CHARACTERISTIC_LENGTH, 
                             defectype = ['I', 'V']
                             ):
        filename = 'generate N = ' + str(N) + ' box = ' + BOX_SHAPE + ' L = ' + str(CHARACTERISTIC_LENGTH)
        datafiles = os.listdir('./data')
        index = 0
        indexedfilename = filename + '.txt'
        while indexedfilename in datafiles:
            index += 1
            indexedfilename = filename + ' (' + str(index) + ').txt'
        with open('data/' + indexedfilename, 'a') as f:
            print(N, file = f)
            for i in range(N):
                flag = np.random.randint(len(defectype))
                x = np.random.random_sample()
                y = np.random.random_sample()
                z = np.random.random_sample()
                print('%d %s %f %f %f'%(i+1, 
                                        defectype[flag], 
                                        x*bound[1], 
                                        y*bound[3], 
                                        z*bound[5]
                                        ), file = f)
        return self.read_defect_data(indexedfilename)

    def encode_defect(self, raw_defect_data):
        initial_defect_type = {}
        defect_type_serial = 1
        for i in raw_defect_data:
            if i[1] not in initial_defect_type.keys():
                initial_defect_type[i[1]] = defect_type_serial
                defect_type_serial += 1
        defect_data = np.empty((raw_defect_data.shape[0], 5), dtype = np.float16)
        for i in range(len(defect_data)):
            for j in range(len(defect_data[i])):
                if j == 1:
                    defect_data[i][j] = initial_defect_type[raw_defect_data[i][j]]
                else:
                    defect_data[i][j] = raw_defect_data[i][j]
        print(defect_data, defect_data.shape)
        return defect_data

if __name__ == '__main__':
    d = Defect()
