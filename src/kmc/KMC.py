import os
import sys

import numpy as np

from defect import Defect

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self):
        # TODO
        pass

    BOX_SHAPE = ''
    CHARACTERISTIC_LENGTH = 0
    SIMULATION_TIME = 0
    TEMPERATURE = 0
    DEFECT = None
    INITIAL_DEFECT_TYPE = None

    def set_up_box(self, shape: str, L: float):
        self.BOX_SHAPE = shape
        self.CHARACTERISTIC_LENGTH = L

    def set_simulation_time(self, SIMULATION_TIME: float):
        self.SIMULATION_TIME = SIMULATION_TIME

    def get_bound(self):
        if self.BOX_SHAPE == 'cube':
            return (
                0, self.CHARACTERISTIC_LENGTH,
                0, self.CHARACTERISTIC_LENGTH,
                0, self.CHARACTERISTIC_LENGTH
                )
        if self.BOX_SHAPE == 'other':
            # TODO
            pass

    def simulation(self):
        t = 0
        while t <= self.TEMPERATURE:
            s = np.random.random_sample()
            r = np.random.random_sample()

        pass


if __name__ == '__main__':
    simulator = KMC()
    simulator.set_up_box('cube', 10)
