import time

import numba
import numpy as np

from config import DefectConfig


class RateManager:
    def __init__(self, DEFECT, INITIAL_DEFECT_TYPE, TEMPERATURE):

        self.DEFECT = DEFECT
        self.INITIAL_DEFECT_TYPE = INITIAL_DEFECT_TYPE
        self.TEMPERATURE = TEMPERATURE
        self.DEFECT_CONFIG = DefectConfig.read()
        self.kB = 1.380649e-23
        self.eV = 1.602e-19
        self.migration_rate_filter()

    def migration_rate_filter(self):

        migration_list = []
        for defect_type in self.DEFECT_CONFIG:
            if 'migration' in self.DEFECT_CONFIG[defect_type].keys():
                mig = [
                    self.INITIAL_DEFECT_TYPE[defect_type],
                    self.DEFECT_CONFIG[defect_type]['migration']['E'],
                    self.DEFECT_CONFIG[defect_type]['migration']['L'],
                    self.DEFECT_CONFIG[defect_type]['migration']['v0']
                ]
                migration_list.append(mig)
        migration_array = np.array(migration_list)
        self.MIGRATION_RATE = migration_array

    def calculate_migration_rate(self):
        tstart = time.time()
        Rm = self.calculate_migration_rate_jit(self.DEFECT, self.MIGRATION_RATE, self.eV, self.kB,
                                               self.TEMPERATURE)
        tend = time.time()
        print(tend - tstart)
        return Rm

    @staticmethod
    @numba.njit(numba.float64[:, :](numba.float64[:, :], numba.float64[:, :], numba.float64, numba.float64, numba.float64))
    def calculate_migration_rate_jit(DEFECT, MIGRATION_RATE, eV, kB, TEMPERATURE):

        init = True

        for defect in DEFECT:
            row_number = 0
            for i in MIGRATION_RATE[:, 0]:
                if defect[1] == i:
                    defect_info = MIGRATION_RATE[row_number, :]
                    break
                else:
                    row_number += 1
            rate = defect_info[3] * np.exp(-defect_info[1] * eV / (kB * TEMPERATURE))
            if init:
                Rm = np.array([[defect[0], rate]])
                init = False
            else:
                Rm = np.append(Rm, np.array([[defect[0], rate]]), axis=0)

        return Rm

    def calculate_total_rate(self):

        # TODO
        pass


if __name__ == '__main__':
    pass
