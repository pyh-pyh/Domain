import numpy as np
import globalvar as gl
from spatio import searchmaterial


class MP:
    def __init__(self, ID, defect_type, x = None, y = None, z = None):
        self.ID = ID
        self.defect_type = defect_type
        self.material = searchmaterial(x, y, z)
        self.x = x
        self.y = y
        self.z = z
        lmig = gl.get_value(self.material + '.' + 'MP.lmig')
        self.l = lmig[defect_type]

    
    def rate(self, temp):
        kB  = 1.380649e-23
        eV  = 1.602e-19
        v0  = gl.get_value(self.material + '.' + 'MP.v0')
        Em  = gl.get_value(self.material + '.' + 'MP.Em')
        Ebk = gl.get_value(self.material + '.' + 'MP.Ebk')
        Eft = gl.get_value(self.material + '.' + 'MP.Eft')

        
        # Rate of each type of defect
        vm = v0*np.exp(-Em[self.defect_type] * eV /(kB * temp))
        vbk = v0*np.exp(-Ebk[self.defect_type] * eV /(kB * temp))
        vft = v0*np.exp(-Eft[self.defect_type] * eV /(kB * temp))
        
        return [vm, vbk, vft]

    pass


class ED:
    def __init__(self, ID, defect_type, x = None, y = None, z = None):
        self.ID = ID
        self.defect_type = defect_type
        self.material = searchmaterial(x, y, z)
        self.x = x
        self.y = y
        self.z = z
        lmig = gl.get_value(self.material + '.' + 'ED.lmig')
        self.l = lmig[defect_type]
    
    
    def rate(self, temp):
        kB = 1.380649e-23
        eV = 1.602e-19
        v0 = gl.get_value(self.material + '.' + 'ED.v0')
        Em = gl.get_value(self.material + '.' + 'ED.Em')
        
        # Rate of each type of defect
        vm = v0*np.exp(-Em[self.defect_type]*eV /(kB*temp))
        
        return [vm, 0, 0]

    pass


class Int:
    def __init__(self, ID, defect_type, x = None, y = None, z = None, stay = []):
        self.ID = ID
        self.defect_type = defect_type
        self.x = x
        self.y = y
        self.z = z
        self.stay = stay


    def absorb(self, obj):
        self.stay.append(obj)


    def rate(self):
        
        return [0, 0, 0]