import numpy as np
import time
import numba

class KMC:
    def __init__(self):
        #TODO
        pass

    def read_defect_data(self, filename):
        defect_data = np.loadtxt('data/' + filename, dtype = [('ID', 'i4'), ('type', np.str, 10), ('x', 'f4'), ('y', 'f4'), ('z', 'f4')], skiprows = 1)
        return defect_data

    def generate_defect_data(self, N, bound, defectype = ['I', 'V']):
        with open('data/generate.txt','w') as f:
            print(N, file = f)
            for i in range(N):
                flag = np.random.randint(len(defectype))
                x = np.random.random_sample()
                y = np.random.random_sample()
                z = np.random.random_sample()
                print('%d %s %f %f %f'%(i+1, defectype[flag], x*bound[1], y*bound[3], z*bound[5]), file = f)
        get_defect_data('generate.txt')

    def simulation(self):
        #
        pass

k = KMC()
t1 = time.time()
d = k.read_defect_data('PKA.txt')
t2 = time.time()
print(d)
print(t2-t1)

