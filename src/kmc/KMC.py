import numpy as np
import os
import sys
import time
import numba

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self):
        #TODO
        pass
    
    BOX_SHAPE = ''
    CHARACTERISTIC_LENGTH = 0
    SIMULATION_TIME = 0
    TEMPERATURE = 0
    DEFECT = None
    INITIAL_DEFECT_TYPE = None

    def set_up_box(self, shape:str, L:float):
        self.BOX_SHAPE = shape
        self.CHARACTERISTIC_LENGTH = L
    
    def set_simulation_time(self, time:float):
        self.SIMULATION_TIME = time
        
    def get_bound(self):        
        if self.BOX_SHAPE == 'cube':
            return (
                0, self.CHARACTERISTIC_LENGTH, 
                0, self.CHARACTERISTIC_LENGTH, 
                0, self.CHARACTERISTIC_LENGTH
                )
        if self.BOX_SHAPE == 'other':
            #TODO
            pass

    def read_defect_data(self, filename):
        raw_defect_data = np.loadtxt('data/' + filename, dtype = [('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')], skiprows = 1)
        defect_data = self.encode_defect(raw_defect_data)
        self.DEFECT = defect_data
        return defect_data

    def generate_defect_data(self, N, defectype = ['I', 'V']):
        bound = self.get_bound()
        filename = 'generate N = ' + str(N) + ' box = ' + self.BOX_SHAPE + ' L = ' + str(self.CHARACTERISTIC_LENGTH)
        datafiles = os.listdir('./data')
        index = 0
        indexedfilename = filename + '.txt'
        while (indexedfilename in datafiles):
            index += 1
            indexedfilename = filename + ' (' + str(index) + ').txt'
        with open('data/' + indexedfilename, 'a') as f:
            print(N, file = f)
            for i in range(N):
                flag = np.random.randint(len(defectype))
                x = np.random.random_sample()
                y = np.random.random_sample()
                z = np.random.random_sample()
                print('%d %s %f %f %f'%(i+1, defectype[flag], x*bound[1], y*bound[3], z*bound[5]), file = f)
        return self.read_defect_data(indexedfilename)

    def encode_defect(self, raw_defect_data):
        initial_defect_type = {}
        defect_type_serial = 1
        for i in raw_defect_data:
            if i[1] not in initial_defect_type.keys():
                initial_defect_type[i[1]] = defect_type_serial
                defect_type_serial += 1
        self.INITIAL_DEFECT_TYPE = initial_defect_type
        defect_data = np.empty((raw_defect_data.shape[0], 5), dtype = np.float16)
        for i in range(len(defect_data)):
            for j in range(len(defect_data[i])):
                if j == 1:
                    defect_data[i][j] = initial_defect_type[raw_defect_data[i][j]]
                else:
                    defect_data[i][j] = raw_defect_data[i][j]
        print(defect_data, defect_data.shape)
        return defect_data

        

        

    def simulation(self):
        t = 0
        while t <= self.TEMPERATURE:
            s = np.random.random_sample()
            r = np.random.random_sample()

        pass

if __name__ == '__main__':
    simulator = KMC()
    simulator.set_up_box('cube', 10)
    data = simulator.generate_defect_data(100)
    print(data.shape)

