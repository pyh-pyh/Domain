import os
import sys

import numpy as np

from defect import DefectManager
from rate import RateManager
from config import SimulationConfig

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class KMC:
    def __init__(self, SIMULATION_TIME=float(0), TEMPERATURE=float(0)):

        self.SIMULATION_TIME = SIMULATION_TIME
        self.TEMPERATURE = TEMPERATURE
        self.BOX_SHAPE = SimulationConfig.read_simulation_box_config()['box_shape']
        self.CHARACTERISTIC_LENGTH = SimulationConfig.read_simulation_box_config(
        )['characteristic_length']
        self.DEFECT = None

    def set_simulation_time(self, SIMULATION_TIME: float):

        self.SIMULATION_TIME = SIMULATION_TIME

    def set_temperature(self, TEMPERATURE: float):

        self.TEMPERATURE = TEMPERATURE

    def get_bound(self):

        if self.BOX_SHAPE == 'cube':
            return (0, self.CHARACTERISTIC_LENGTH, 0, self.CHARACTERISTIC_LENGTH, 0,
                    self.CHARACTERISTIC_LENGTH)
        if self.BOX_SHAPE == 'other':
            # TODO other shape of simulation box
            pass

    def simulation(self):

        defect_manager = DefectManager()
        self.DEFECT = defect_manager.DEFECT

        rate_manager = RateManager(self.DEFECT, self.TEMPERATURE)
        print(rate_manager.calculate_migration_rate())

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
                    # TODO execute defect event
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
    simulator = KMC(SIMULATION_TIME=10, TEMPERATURE=300)
    simulator.simulation()
