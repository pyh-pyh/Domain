import os
import sys

import numpy as np

from defect import Defect

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self, BOX_SHAPE='', CHARACTERISTIC_LENGTH=float(0), SIMULATION_TIME=float(0), TEMPERATURE=float(0)):
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
            return (0, self.CHARACTERISTIC_LENGTH, 0, self.CHARACTERISTIC_LENGTH, 0, self.CHARACTERISTIC_LENGTH)
        if self.BOX_SHAPE == 'other':
            # TODO
            pass

    def simulation(self):
        defect_manager = Defect()
        self.DEFECT = defect_manager.initialize_defect()
        t = 0
        while t <= self.SIMULATION_TIME:
            s = np.random.random_sample()
            r = np.random.random_sample()

        pass


if __name__ == '__main__':
    simulator = KMC()
    simulator.set_up_box('cube', 10)
    simulator.simulation()
