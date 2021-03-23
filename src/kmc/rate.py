import time

import numba as nb
import numpy as np

from configs import DefectConfig, SimulationConfig

load_start = time.time()


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
        self.Rm = None
        self.Rr = None
        self.Rn = None

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
                    repeated = False
                    for reactions in recombination_list:
                        if self.DEFECT_TYPE_CONFIG[defect_type] == reactions[
                                1] and self.DEFECT_TYPE_CONFIG[self.DEFECT_CONFIG[defect_type][
                                    'recombination']['object']] == reactions[0]:
                            repeated = True
                    if not repeated:
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
                        repeated = False
                        for reactions in recombination_list:
                            if self.DEFECT_TYPE_CONFIG[defect_type] == reactions[
                                    1] and self.DEFECT_TYPE_CONFIG[
                                        reaction['object']] == reactions[0]:
                                repeated = True
                        if not repeated:
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
        print('migration calculate time', tend - tstart)
        self.Rm = Rm
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

        neighbor = NeighborSearcher(self.DEFECT, self.RECOMBINATION_RATE, self.TEMPERATURE)
        Rr = neighbor.calculate_recombination_rate()
        self.Rr = Rr
        return Rr

    def calculate_total_rate(self):

        Rm = self.calculate_migration_rate()
        Rm = np.append(Rm, np.zeros((Rm.shape[0],1)), axis=1)
        Rr = self.calculate_recombination_rate()
        Rn = np.append(Rm, Rr, axis=0)
        self.Rn = Rn
        return Rn


class NeighborSearcher:
    def __init__(self, DEFECT, RECOMBINATION_RATE, TEMPERATURE):

        self.kB = 1.380649e-23
        self.eV = 1.602e-19
        self.DEFECT = DEFECT
        self.TEMPERATURE = TEMPERATURE
        self.RECOMBINATION_RATE = RECOMBINATION_RATE
        self.SIMULATION_BOX = SimulationConfig.read_simulation_box_config()
        self.initial_space_mesh()

    def calculate_recombination_rate(self):

        tstart = time.time()
        Rr = self.calculate_recombination_rate_jit(self.SPACE_MESH, self.RECOMBINATION_RATE,
                                                   self.eV, self.kB, self.TEMPERATURE)
        tend = time.time()
        print('recombination calculate time ', tend - tstart)
        return Rr

    @staticmethod
    @nb.njit(nb.float64[:, :](nb.float64[:, :], nb.float64[:, :], nb.float64, nb.float64,
                              nb.float64))
    def calculate_recombination_rate_jit(SPACE_MESH, RECOMBINATION_RATE, eV, kB, TEMPERATURE):

        init = True

        for i, defect1 in enumerate(SPACE_MESH[:-1, :]):
            for defect2 in SPACE_MESH[i + 1:, :]:

                # TODO neighborhood mesh defect can react
                if defect1[5] == defect2[5]:
                    valid_reaction = False
                    for j, reaction in enumerate(RECOMBINATION_RATE[:, :2]):
                        if np.array([defect1[1], defect2[1]]).all() == reaction.all() or np.array(
                            [defect2[1], defect1[1]]).all() == reaction.all():
                            valid_reaction = True
                            reaction_number = j
                            break

                    if valid_reaction:
                        distance = np.sqrt(np.sum((defect1[2:5] - defect2[2:5])**2))

                        if distance <= RECOMBINATION_RATE[reaction_number, 4]:
                            rate = RECOMBINATION_RATE[reaction_number, 3] * np.exp(
                                -RECOMBINATION_RATE[reaction_number, 2] * eV / (kB * TEMPERATURE))
                            if init:
                                Rr = np.array([[rate, defect1[0], defect2[0]]])
                                init = False
                            else:
                                Rr = np.append(Rr,
                                               np.array([[rate, defect1[0], defect2[0]]]),
                                               axis=0)
        return Rr

    def initial_space_mesh(self, mesh_length: float = 5):

        box_length = self.SIMULATION_BOX['box_length']
        mesh_number_each_edge = int(box_length // mesh_length - 1)
        digit = int(np.log10(mesh_number_each_edge)) + 1
        mesh_length_array = np.array([1, 1, mesh_length, mesh_length, mesh_length])
        defect_belong_to = self.DEFECT // mesh_length_array
        self.SPACE_MESH = np.c_[self.DEFECT, defect_belong_to[:, 2] * (10**(2 * digit)) +
                                defect_belong_to[:, 3] * (10**(digit)) + defect_belong_to[:, 4]]


load_end = time.time()
print('rate compile time ', load_end - load_start)
if __name__ == '__main__':
    pass
