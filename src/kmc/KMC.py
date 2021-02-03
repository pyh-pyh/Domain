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

    def set_up_box(self, shape:str, L:float):
        ''''''
        self.BOX_SHAPE = shape
        self.CHARACTERISTIC_LENGTH = L
        
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
        defect_data = np.loadtxt('data/' + filename, dtype = [('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')], skiprows = 1)
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

    def simulation(self):
        #
        pass

if __name__ == '__main__':

