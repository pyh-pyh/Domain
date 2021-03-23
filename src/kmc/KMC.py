import os
import sys
import time

import numba as nb
import numpy as np

from configs import SimulationConfig
from defect import DefectManager
from rate import RateManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self, SIMULATION_TIME=float(0), TEMPERATURE=float(0)):

        tstart = time.time()
        self.SIMULATION_TIME = SIMULATION_TIME
        self.TEMPERATURE = TEMPERATURE
        self.BOX_SHAPE = SimulationConfig.read_simulation_box_config()['box_shape']
        self.BOX_LENGTH = SimulationConfig.read_simulation_box_config()['box_length']
        self.DEFECT = None
        tend = time.time()
        print('KMC init time ', tend - tstart)

    def set_simulation_time(self, SIMULATION_TIME: float):

        self.SIMULATION_TIME = SIMULATION_TIME

    def set_temperature(self, TEMPERATURE: float):

        self.TEMPERATURE = TEMPERATURE

    def get_bound(self):

        if self.BOX_SHAPE == 'cube':
            return (0, self.BOX_LENGTH, 0, self.BOX_LENGTH, 0, self.BOX_LENGTH)
        if self.BOX_SHAPE == 'other':
            # TODO other shape of simulation box
            pass

    @staticmethod
    @nb.njit(nb.int32(nb.float64[:, :], nb.float64))
    def find_react(RN, r):

        point = len(RN) // 2
        up = len(RN)
        down = 0
        while True:
            if (np.sum(RN[:point, 0]) <= r * np.sum(RN[:, 0])) and (np.sum(
                    RN[:(point + 1) % (len(RN) + 1), 0]) > r * np.sum(RN[:, 0])):
                return point

            if np.sum(RN[:point, 0]) > r * np.sum(RN[:, 0]):
                up = point
                point = int((up + down) / 2)
                continue

            if np.sum(RN[:(point + 1) % (len(RN) + 1), 0]) < r * np.sum(RN[:, 0]):
                down = point
                point = int((up + down) / 2)
                continue

    def simulation(self):

        tstart_defect = time.time()
        defect_manager = DefectManager()
        self.DEFECT = defect_manager.DEFECT
        tend_defect = time.time()
        print('defect init time ', tend_defect - tstart_defect)

        tstart_rate = time.time()
        rate_manager = RateManager(self.DEFECT, self.TEMPERATURE)
        tend_rate = time.time()
        print('rate init time ', tend_rate - tstart_rate)

        t = 0
        circulation = 0

        while t <= self.SIMULATION_TIME:
            circulation_start_time = time.time()
            s = np.random.random_sample()
            r = np.random.random_sample()
            RN = rate_manager.calculate_total_rate()
            point = self.find_react(RN, r)

            dt = -np.log(s) / np.sum(RN[:, 0])
            t += dt
            circulation += 1
            circulation_end_time = time.time()
            print('circulation ' + str(circulation) + ' time ',
                  circulation_end_time - circulation_start_time)


if __name__ == '__main__':
    simulator = KMC(SIMULATION_TIME=10, TEMPERATURE=300)
    simulator.simulation()
