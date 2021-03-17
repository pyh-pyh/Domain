import json
import os


class DefectConfig:
    @staticmethod
    def write(path='./config', file_name='/defect_config.json', **kwargs):
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
                                        defect_config[i][j] = [defect_config[i][j], kwargs[i][j]]
                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], dict) and (kwargs[i][j]
                                                                     not in defect_config[i][j]):
                                        defect_config[i][j].append(kwargs[i][j])
                                    if isinstance(defect_config[i][j], dict) and isinstance(
                                            kwargs[i][j], list) and (defect_config[i][j]
                                                                     not in kwargs[i][j]):
                                        defect_config[i][j] = kwargs[i][j].append(
                                            defect_config[i][j])
                                    if isinstance(defect_config[i][j], list) and isinstance(
                                            kwargs[i][j], list):
                                        temp = [
                                            kwelement for kwelement in kwargs[i][j]
                                            if kwelement not in defect_config[i][j]
                                        ]
                                        defect_config[i][j] += temp

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


if __name__ == '__main__':
    DefectConfig.write(V={
        'migration': {
            'E': 5,
            'L': 1,
            'v0':1
        },
        'recombination': {
            'object': 'I',
            'E': 2
        }
    },
                       I={
                           'migration': {
                               'E': 0.5,
                               'L': 1,
                               'v0':1
                           },
                           'recombination': [{
                               'object': 'I',
                               'E': 0.5
                           }, {
                               'object': 'V',
                               'E': 2
                           }]
                       })
    con = DefectConfig.read()
    print(con['I'])
