import os
import sys

import numpy as np

from defect import DefectManager
from rate import RateManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self,
                 BOX_SHAPE='',
                 CHARACTERISTIC_LENGTH=float(0),
                 SIMULATION_TIME=float(0),
                 TEMPERATURE=float(0)):

        self.BOX_SHAPE = BOX_SHAPE
        self.CHARACTERISTIC_LENGTH = CHARACTERISTIC_LENGTH
        self.SIMULATION_TIME = SIMULATION_TIME
        self.TEMPERATURE = TEMPERATURE

    def set_up_box(self, shape: str, L: float):

        self.BOX_SHAPE = shape
        self.CHARACTERISTIC_LENGTH = L

    def set_simulation_time(self, SIMULATION_TIME: float):

        self.SIMULATION_TIME = SIMULATION_TIME

    def get_bound(self):

        if self.BOX_SHAPE == 'cube':
            return (0, self.CHARACTERISTIC_LENGTH, 0, self.CHARACTERISTIC_LENGTH, 0,
                    self.CHARACTERISTIC_LENGTH)
        if self.BOX_SHAPE == 'other':
            # TODO
            pass

    def simulation(self):

        defect_manager = DefectManager()
        self.DEFECT = defect_manager.initialize_defect()
        self.INITIAL_DEFECT_TYPE = defect_manager.INITIAL_DEFECT_TYPE

        rate_manager = RateManager(self.DEFECT, self.TEMPERATURE)
        t = 0
        while t <= self.SIMULATION_TIME:
            s = np.random.random_sample()
            r = np.random.random_sample()
            RN = rate_manager.RN
            point = len(RN) // 2
            up = len(RN)
            down = 0

            while True:
                if (sum(RN[:point]) <= r * sum(RN)) and (sum(RN[:(point + 1) %
                                                                (len(RN) + 1)]) > r * sum(RN)):
                    # TODO
                    dt = -np.log(s) / sum(RN)
                    t += dt
                    break

                if sum(RN[:point]) > r * sum(RN):
                    up = point
                    point = int((up + down) / 2)
                    continue

                if sum(RN[:(point + 1) % (len(RN) + 1)]) < r * sum(RN):
                    down = point
                    point = int((up + down) / 2)
                    continue


if __name__ == '__main__':
    simulator = KMC()
    simulator.set_up_box('cube', 10)
    simulator.simulation()
