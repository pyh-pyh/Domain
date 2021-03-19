import time

import numba as nb
import numpy as np

from config import DefectConfig, SimulationConfig


class RateManager:
    def __init__(self, DEFECT, TEMPERATURE):

        self.kB = 1.380649e-23
        self.eV = 1.602e-19
        self.DEFECT = DEFECT
        self.TEMPERATURE = float(TEMPERATURE)
        self.DEFECT_CONFIG = DefectConfig.read()
        self.DEFECT_TYPE_CONFIG = SimulationConfig.read_defect_type_config()
        self.migration_rate_filter()
        self.recombination_rate_filter()

    def migration_rate_filter(self):

        migration_list = []
        for defect_type in self.DEFECT_CONFIG:
            if 'migration' in self.DEFECT_CONFIG[defect_type].keys():
                mig = [
                    self.DEFECT_TYPE_CONFIG[defect_type],
                    self.DEFECT_CONFIG[defect_type]['migration']['E'],
                    self.DEFECT_CONFIG[defect_type]['migration']['v0']
                ]
                migration_list.append(mig)
        migration_array = np.array(migration_list, dtype=np.float64)
        self.MIGRATION_RATE = migration_array

    def recombination_rate_filter(self):

        recombination_list = []
        for defect_type in self.DEFECT_CONFIG:
            if 'recombination' in self.DEFECT_CONFIG[defect_type].keys():
                if isinstance(self.DEFECT_CONFIG[defect_type]['recombination'], dict):
                    recomb = [
                        self.DEFECT_TYPE_CONFIG[defect_type], self.DEFECT_TYPE_CONFIG[
                            self.DEFECT_CONFIG[defect_type]['recombination']['object']],
                        self.DEFECT_CONFIG[defect_type]['recombination']['E'],
                        self.DEFECT_CONFIG[defect_type]['recombination']['v0'],
                        self.DEFECT_CONFIG[defect_type]['recombination']['L']
                    ]
                    recombination_list.append(recomb)
                if isinstance(self.DEFECT_CONFIG[defect_type]['recombination'], list):
                    recomb = []
                    for reaction in self.DEFECT_CONFIG[defect_type]['recombination']:
                        recomb.append([
                            self.DEFECT_TYPE_CONFIG[defect_type],
                            self.DEFECT_TYPE_CONFIG[reaction['object']], reaction['E'],
                            reaction['v0'], reaction['L']
                        ])
                    recombination_list += recomb
        recombination_array = np.array(recombination_list)
        self.RECOMBINATION_RATE = recombination_array

    def calculate_migration_rate(self):

        tstart = time.time()
        Rm = self.calculate_migration_rate_jit(self.DEFECT, self.MIGRATION_RATE, self.eV, self.kB,
                                               self.TEMPERATURE)
        tend = time.time()
        print(tend - tstart)
        return Rm

    @staticmethod
    @nb.njit(nb.float64[:, :](nb.float64[:, :], nb.float64[:, :], nb.float64, nb.float64,
                              nb.float64))
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
            rate = defect_info[2] * np.exp(-defect_info[1] * eV / (kB * TEMPERATURE))
            if init:
                Rm = np.array([[rate, defect[0]]])
                init = False
            else:
                Rm = np.append(Rm, np.array([[rate, defect[0]]]), axis=0)

        return Rm

    def calculate_recombination_rate(self):

        tstart = time.time()
        Rr = self.calculate_migration_rate_jit(self.DEFECT, self.RECOMBINATION_RATE, self.eV,
                                               self.kB, self.TEMPERATURE)
        tend = time.time()
        print(tend - tstart)
        return Rr

    @staticmethod
    @nb.njit(nb.float64[:, :](nb.float64[:, :], nb.float64[:, :], nb.float64, nb.float64,
                              nb.float64))
    def calculate_recombination_rate_jit(DEFECT, RECOMBINATION_RATE, eV, kB, TEMPERATURE):

        # TODO add neighbor searching
        return Rr

    def calculate_total_rate(self):

        # TODO
        pass


class NeighborSearcher:
    def __init__(self, DEFECT, RECOMBINATION_RATE):
        
        self.DEFECT = DEFECT
        self.RECOMBINATION_RATE = RECOMBINATION_RATE
        
    def search_for_potential_reactions(self):
        
        # TODO
        pass
    
    def initial_space_mesh(self):
        
        
        


if __name__ == '__main__':
    pass
