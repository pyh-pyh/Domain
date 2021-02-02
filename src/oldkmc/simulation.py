import globalvar as gl
import numpy as np
import time
from spatio import search, searchmaterial
from defect import Int


def idmanager(initial = 'no'):
    '''Record ID'''
    defect = gl.get_value('defect')
    if initial == 'yes':
        gl.set_value('idm', len(defect)+1)
    if initial == 'no':
        idm = gl.get_value('idm')
        idm += 1
        gl.set_value('idm', idm)
        
        return idm-1


def recombrate(obj1, obj2):
    '''Calculate the recombination rate between two defects'''
    kB = 1.380649e-23
    eV = 1.602e-19
    material = searchmaterial(obj1.x, obj1.y, obj1.z)
    v0 = gl.get_value(material + '.' + 'MP.v0')
    temperature = gl.get_value('temperature')
    Ere = gl.get_value(material + '.' + 'Ere')
    try:
        rate = v0*np.exp(-Ere[obj1.defect_type + '+' + obj2.defect_type][1]*eV /(kB*temperature))
    except KeyError:
        rate = v0*np.exp(-Ere[obj2.defect_type + '+' + obj1.defect_type][1]*eV /(kB*temperature))
    
    return rate


def recomblist(obj):
    '''Add one obj's recombination rate to the list of recombination rates'''
    Rre = gl.get_value('Rre')
    Rint = gl.get_value('Rint')
    material = searchmaterial(obj.x, obj.y, obj.z)
    Ere = gl.get_value(material + '.' + 'Ere')
    reactions = list(Ere.keys())
    nei = search(obj)
    neipar = nei[0]
    neint = nei[1]
    if neipar != []:
        for i in range(len(neipar)):
            if (obj.defect_type + '+' + neipar[i].defect_type not in reactions) and (neipar[i].defect_type + '+' + obj.defect_type not in reactions):
                continue
            rate = recombrate(obj, neipar[i])
            if rate != 0 and ([rate, neipar[i].ID - 1, obj.ID - 1] not in Rre) and ([rate, obj.ID - 1, neipar[i].ID - 1] not in Rre):
                Rre.append([rate, obj.ID - 1, neipar[i].ID - 1])
    gl.set_value('Rre', Rre)
    
    if obj.defect_type + '+Int' in reactions:
        if neint != []:
            for i in range(len(neint)):
                rate = intrate(obj)
                if rate != 0 and ([rate, neint[i].ID - 1, obj.ID - 1] not in Rint) and ([rate, obj.ID - 1, neint[i].ID - 1] not in Rint):
                    Rint.append([rate, obj.ID - 1, neint[i].ID - 1])
    gl.set_value('Rint', Rint)

    pass


def intrate(obj):
    '''Calculate the recombination rate between two defects'''
    kB = 1.380649e-23
    eV = 1.602e-19
    material = searchmaterial(obj.x, obj.y, obj.z)
    v0 = gl.get_value(material + '.' + 'MP.v0')
    temperature = gl.get_value('temperature')
    Ere = gl.get_value(material + '.' + 'Ere')
    rate = v0*np.exp(-Ere[obj.defect_type + '+Int'][1]*eV /(kB*temperature))

    return rate


def clearecomb(j):
    '''Clear one defect's recombination rate'''
    Rre = gl.get_value('Rre')
    result = []
    for i in range(len(Rre)):
        if Rre[i][1] == j or Rre[i][2] == j:
            result.append(i)
    if result != []:
        x = 0
        for i in result:
            del Rre[i - x]
            x += 1
    gl.set_value('Rre', Rre)

    pass


def cleabsorb(j):
    '''Clear one defect's absoption rate'''
    Rint = gl.get_value('Rint')
    result = []
    for i in range(len(Rint)):
        if Rint[i][1] == j:
            result.append(i)
    if result != []:
        x = 0
        for i in result:
            del Rint[i - x]
            x += 1
    gl.set_value('Rint', Rint)

    pass


def searchint():
    '''Search for interface'''
    lattice = gl.get_value('lattice')
    intx = [[] for i in range(len(lattice[0][0]))]
    inty = [[] for i in range(len(lattice[0]))]
    intz = [[] for i in range(len(lattice))]
    interface = []
    interlist = []
    i = 1
    for z in range(len(lattice)):
        for y in range(len(lattice[0])):
            for x in range(len(lattice[0][0])):
                
                if lattice[z][y][x] != lattice[z][y][(x+1) % len(lattice[0][0])]:
                    intx[x].append([y, z])
                    interlist.append(['x', x, y, z])
                    interface.append(Int(i, 'x', x = x, y = y, z = z))
                    i += 1
                
                if lattice[z][y][x] != lattice[z][(y+1) % len(lattice[0])][x]:
                    inty[y].append([x, z])
                    interlist.append(['y', x, y, z])
                    interface.append(Int(i, 'y', x = x, y = y, z = z))
                    i += 1
                
                if lattice[z][y][x] != lattice[(z+1) % len(lattice)][y][x]:
                    intz[z].append([x, y])
                    interlist.append(['z', x, y, z])
                    interface.append(Int(i, 'z', x = x, y = y, z = z))
                    i += 1
    
    inter_mesh = []
    inter_mesh.append(intx)
    inter_mesh.append(inty)
    inter_mesh.append(intz)
    gl.set_value('interlist', interlist)
    gl.set_value('inter_mesh', inter_mesh)
    gl.set_value('interface', interface)

    pass

