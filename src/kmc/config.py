import json
import os


class DefectConfig:
    @staticmethod
    def write(path='./config', file_name='/defect_config.json', **kwargs):
        '''You should input defects' config in this format:
        I={
            'migration': {
                'E': 5,
                'L': 1,
                'v0': 1
            },
            'recombination': [{
                'object': 'V',
                'E': 1,
                'v0': 1,
                'L': 1,
                'creation': 'None'
            }, {
                'object': 'I',
                'E': 1.5,
                'v0': 1,
                'L': 1,
                'creation': 'I2'
            }]
        }
        '''
        size = os.path.getsize(path + file_name)
        if size != 0:
            with open(path + file_name, 'r+') as f:
                defect_config = json.load(f)
                for i in kwargs:
                    if i not in defect_config.keys():
                        defect_config[i] = kwargs[i]
                    else:
                        for j in kwargs[i]:
                            if j not in defect_config[i].keys():
                                defect_config[i][j] = kwargs[i][j]
                            else:
                                if j == 'recombination':

                                    if isinstance(defect_config[i][j], dict) and isinstance(
                                            kwargs[i][j],
                                            dict) and defect_config[i][j] != kwargs[i][j]:
                                        if defect_config[i][j]['object'] == kwargs[i][j]['object']:
                                            defect_config[i][j] = kwargs[i][j]
                                        else:
                                            defect_config[i][j] = [
                                                defect_config[i][j], kwargs[i][j]
                                            ]

                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], dict) and (kwargs[i][j]
                                                                     not in defect_config[i][j]):
                                        found = False
                                        for k, l in enumerate(defect_config[i][j]):
                                            if l['object'] == kwargs[i][j]['object']:
                                                defect_config[i][j][k] = kwargs[i][j]
                                                found = True
                                        if not found:
                                            defect_config[i][j].append(kwargs[i][j])

                                    if isinstance(defect_config[i][j], dict) and isinstance(
                                            kwargs[i][j], list) and (defect_config[i][j]
                                                                     not in kwargs[i][j]):
                                        found = False
                                        for k, l in enumerate(kwargs[i][j]):
                                            if l['object'] == defect_config[i][j]['object']:
                                                defect_config[i][j] = kwargs[i][j]
                                                found = True
                                        if not found:
                                            defect_config[i][j] = kwargs[i][j].append(
                                                defect_config[i][j])

                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], list):
                                        kwkeys = [kwelement['object'] for kwelement in kwargs[i][j]]
                                        temp = [
                                            kwelement for kwelement in defect_config[i][j]
                                            if kwelement['object'] not in kwkeys
                                        ]
                                        defect_config[i][j] = kwargs[i][j] + temp

                                else:
                                    defect_config[i][j] = kwargs[i][j]
                f.seek(0)
                f.truncate()
                json.dump(defect_config, f, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            with open(path + file_name, 'w+') as f:
                json.dump(kwargs, f, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def read(path='./config', file_name='/defect_config.json'):

        with open(path + file_name, 'r+') as f:
            defect_config = json.load(f)
        return defect_config


class SimulationConfig:
    @staticmethod
    def write_defect_type_config(path='./config', file_name='/simulation_config.json', **kwargs):

        with open(path + file_name, 'a+') as f:
            f.close()
        size = os.path.getsize(path + file_name)
        if size != 0:
            with open(path + file_name, 'r+') as f:
                simulation_config = json.load(f)
                defect_type_config = simulation_config['defect_type']
                for i in kwargs:
                    defect_type_config[i] = kwargs[i]
                f.seek(0)
                f.truncate()
                json.dump(simulation_config, f, sort_keys=True, indent=4, separators=(',', ': '))

        else:
            with open(path + file_name, 'w+') as f:
                simulation_config = {'defect_type': kwargs}
                json.dump(simulation_config, f, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def read_defect_type_config(path='./config', file_name='/simulation_config.json'):

        with open(path + file_name, 'r+') as f:
            simulation_config = json.load(f)
            defect_type_config = simulation_config['defect_type']
        return defect_type_config

    @staticmethod
    def write_simulation_box_config(box_shape,
                                    characteristic_length,
                                    path='./config',
                                    file_name='/simulation_config.json'):

        with open(path + file_name, 'a+') as f:
            f.close()
        size = os.path.getsize(path + file_name)
        if size != 0:
            with open(path + file_name, 'r+') as f:
                simulation_config = json.load(f)
                if 'simulation_box' not in simulation_config.keys():
                    simulation_config['simulation_box'] = {}
                simulation_box_config = simulation_config['simulation_box']
                simulation_box_config['box_shape'] = box_shape
                simulation_box_config['characteristic_length'] = characteristic_length
                f.seek(0)
                f.truncate()
                json.dump(simulation_config, f, sort_keys=True, indent=4, separators=(',', ': '))

        else:
            with open(path + file_name, 'w+') as f:
                simulation_config = {
                    'simulation_box': {
                        'box_shape': box_shape,
                        'characteristic_length': characteristic_length
                    }
                }
                json.dump(simulation_config, f, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def read_simulation_box_config(path='./config', file_name='/simulation_config.json'):

        with open(path + file_name, 'r+') as f:
            simulation_config = json.load(f)
            simulation_box_config = simulation_config['simulation_box']
        return simulation_box_config


if __name__ == '__main__':
    SimulationConfig.write_defect_type_config(I2=3, V2=4)
    SimulationConfig.write_simulation_box_config('cube', 100)
