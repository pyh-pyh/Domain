import numpy as np
import globalvar as gl
from defect import ED, MP, Int
from simulation import clearecomb, idmanager, recomblist, cleabsorb
from spatio import index, mesh, updateID, searchmaterial, Rmindex


def migrate(point):
    '''Define the event of migration of point defects'''
    # Import parameters
    bound = gl.get_value('bound')
    Rm = gl.get_value('Rm')
    defect_mesh = gl.get_value('defect_mesh')
    defect = gl.get_value('defect')

    # Delete original position and recombination pair
    j = updateID(Rm[point][2] + 1)
    del defect_mesh[index(j)[0]][index(j)[1]]
    clearecomb(defect[j].ID - 1)

    # Choose a direction randomly and migrate
    axis = np.random.randint(0,6)
    if axis == 0:
        defect[j].x = (defect[j].x + defect[j].l - bound[0])%(bound[1] - bound[0]) + bound[0]
    if axis == 1:
        defect[j].x = (defect[j].x - defect[j].l - bound[1])%(bound[0] - bound[1]) + bound[1]
    if axis == 2:
        defect[j].y = (defect[j].y + defect[j].l - bound[2])%(bound[3] - bound[2]) + bound[2]
    if axis == 3:
        defect[j].y = (defect[j].y - defect[j].l - bound[3])%(bound[2] - bound[3]) + bound[3]
    if axis == 4:
        defect[j].z = (defect[j].z + defect[j].l - bound[4])%(bound[5] - bound[4]) + bound[4]
    if axis == 5:
        defect[j].z = (defect[j].z - defect[j].l - bound[5])%(bound[4] - bound[5]) + bound[5]
    
    # Update position and recombination rate
    gl.set_value('defect', defect)
    mesh(defect[j])
    recomblist(defect[j])
    
    pass


def break_up(point):
    '''Define the event of break-up of a pair defect'''
    # Import parameters
    Rm = gl.get_value('Rm')
    Rbk = gl.get_value('Rbk')
    temperature = gl.get_value('temperature')
    defect = gl.get_value('defect')
    defect_mesh = gl.get_value('defect_mesh')

    # Order in list Rbk
    i = point - len(Rm)

    # Order in list defect, means the jth defect is to breakup
    j = Rbk[i][1]

    # Append the defect generated by breaking-up to the end of the list and migrate random walk
    if defect[j].defect_type == 'CV':
        a = MP(ID = int(idmanager()), defect_type = 'V', x = defect[j].x, y = defect[j].y, z = defect[j].z)
    elif defect[j].defect_type == 'CI':
        a = MP(ID = int(idmanager()), defect_type = 'I', x = defect[j].x, y = defect[j].y, z = defect[j].z)
    
    defect.append(a)
    gl.set_value('defect', defect)
    mesh(defect[len(defect) - 1])
    if defect[len(defect) - 1].rate(temperature)[0] != 0:
        Rm.append([defect[len(defect) - 1].rate(temperature)[0], len(defect) - 1])
        gl.set_value('Rm', Rm)
        migrate(len(Rm) - 1)
    
    # Update the defect type
    defect[j].defect_type = 'C'
    gl.set_value('defect', defect)
    defect_mesh[index(j)[0]][index(j)[1]].defect_type = 'C'
    gl.set_value('defect_mesh', defect_mesh)

    pass

    
def franck_turnbull(point):
    '''Define the Franck-Turnbull mechanism'''
    # Import parameters
    Rm = gl.get_value('Rm')
    Rbk = gl.get_value('Rbk')
    Rft = gl.get_value('Rft')
    temperature = gl.get_value('temperature')
    defect = gl.get_value('defect')

    # Order in list Rft
    i = point - len(Rm) - len(Rbk)

    # Order in list defect, means the jth defect is to F-T
    j = Rft[i][1]

    # Append the defect generated by breaking-up to the end of the list and migrate random walk
    a = MP(ID = int(idmanager()), defect_type = 'V', x = defect[j].x, y = defect[j].y, z = defect[j].z)
    defect.append(a)
    gl.set_value('defect', defect)
    mesh(defect[len(defect) - 1])
    Rm.append([defect[len(defect) - 1].rate(temperature)[0], len(defect) - 1])
    gl.set_value('Rm', Rm)
    migrate(len(Rm) - 1)

    pass


def recombine(point):
    '''Define the recombine mechanism'''
    # Import parameters
    Rm = gl.get_value('Rm')
    Rbk = gl.get_value('Rbk')
    Rft = gl.get_value('Rft')
    Rre = gl.get_value('Rre')
    defectype = gl.get_value('defectype')
    defect = gl.get_value('defect')
    defect_mesh = gl.get_value('defect_mesh')
    temperature = gl.get_value('temperature')
    
    # Order in list Rre
    i = point - len(Rm) - len(Rbk) - len(Rft)

    # ID-1 of the selected defects
    idj = Rre[i][1] + 1
    idk = Rre[i][2] + 1
    j = updateID(idj)
    k = updateID(idk)
    material = searchmaterial(defect[j].x, defect[j].y,defect[j].z)
    Ere = gl.get_value(material + '.' + 'Ere')
    
    # Use the first defect's position as the new defect's position
    tempx = defect[j].x
    tempy = defect[j].y
    tempz = defect[j].z

    # Diminish
    if (defect[j].defect_type == 'I' and defect[k].defect_type == 'V') or (defect[j].defect_type == 'V' and defect[k].defect_type == 'I'):
        a = 'Nothing'
    
    # Consult reaction table to determine what reaction to perform
    else:
        if defect[j].defect_type + '+' + defect[k].defect_type in list(Ere.keys()):
            product = Ere[defect[j].defect_type + '+' + defect[k].defect_type][0]
            if product in defectype['MP']:
                a = MP(ID = int(idmanager()), defect_type = product, x = tempx, y = tempy, z = tempz)
            elif product in defectype['ED']:
                a = ED(ID = int(idmanager()), defect_type = product, x = tempx, y = tempy, z = tempz)
        elif defect[k].defect_type + '+' + defect[j].defect_type in list(Ere.keys()):
            product = Ere[defect[k].defect_type + '+' + defect[j].defect_type][0]
            if product in defectype['MP']:
                a = MP(ID = int(idmanager()), defect_type = product, x = tempx, y = tempy, z = tempz)
            elif product in defectype['ED']:
                a = ED(ID = int(idmanager()), defect_type = product, x = tempx, y = tempy, z = tempz)
    
    # Add product
    if a != 'Nothing':
        defect.append(a)
        gl.set_value('defect', defect)
        mesh(defect[len(defect) - 1])
        if defect[len(defect) - 1].rate(temperature)[0] != 0:
            Rm.append([defect[len(defect) - 1].rate(temperature)[0], len(Rm) + 1, defect[len(defect) - 1].ID - 1])
            migrate(len(Rm) - 1)

    # Clear reactant in defect_mesh
    j0 = index(j)[0]
    j1 = index(j)[1]
    k0 = index(k)[0]
    k1 = index(k)[1]
    if j0 == k0:
        if j1 > k1:
            del defect_mesh[j0][j1]
            del defect_mesh[k0][k1]
        if k1 > j1:
            del defect_mesh[k0][k1]
            del defect_mesh[j0][j1]
    if j0 != k0:
        del defect_mesh[j0][j1]
        del defect_mesh[k0][k1]
    gl.set_value('defect_mesh', defect_mesh)

    # Clear reactant in defect
    if j > k:
        del defect[j]
        del defect[k]
        rj = Rmindex(idj-1)
        rk = Rmindex(idk-1)
        if rj != None and rk != None:
            if rj > rk:
                del Rm[rj]
                del Rm[rk]
                for i in range(rk, rj-1):
                    Rm[i][1] -= 1
                for i in range(rj-1, len(Rm)):
                    Rm[i][1] -= 2
            if rj < rk:
                del Rm[rk]
                del Rm[rj]
                for i in range(rj, rk):
                    Rm[i][1] -= 1
                for i in range(rk, len(Rm)):
                    Rm[i][1] -= 2
            
        if rj == None and rk != None:
            del Rm[rk]
            for i in range(rk, len(Rm)):
                Rm[i][1] -= 1
        if rk == None and rj != None:
            del Rm[rj]
            for i in range(rj, len(Rm)):
                Rm[i][1] -= 1
    
    if k > j:
        del defect[k]
        del defect[j]
        rk = Rmindex(idk-1)
        rj = Rmindex(idj-1)
        if rk != None and rj != None:
            del Rm[rk]
            del Rm[rj]
            for i in range(rj, rk):
                Rm[i][1] -= 1
            for i in range(rk, len(Rm)):
                Rm[i][1] -= 2
        if rk == None and rj != None:
            del Rm[rj]
            for i in range(rj, len(Rm)):
                Rm[i][1] -= 1
        if rj == None and rk != None:
            del Rm[rk]
            for i in range(rk, len(Rm)):
                Rm[i][1] -= 1
     
    gl.set_value('defect', defect)
    gl.set_value('Rm', Rm)
    
    # Clear reactant recombination rate and absorption rate
    clearecomb(idj-1)
    clearecomb(idk-1)
    cleabsorb(idj-1)
    cleabsorb(idk-1)

    pass


def absorb(point):
    '''Define the absorption event'''
    # Import parameters
    Rm = gl.get_value('Rm')
    Rbk = gl.get_value('Rbk')
    Rft = gl.get_value('Rft')
    Rre = gl.get_value('Rre')
    Rint = gl.get_value('Rint')
    defect = gl.get_value('defect')
    interface = gl.get_value('interface')
    defect_mesh = gl.get_value('defect_mesh')

    # Update index
    i = point - len(Rm) - len(Rbk) - len(Rft) - len(Rre)
    idj = Rint[i][1] + 1
    j = updateID(idj)
    k = Rint[i][2]

    # Absorb by interface
    material = searchmaterial(defect[j].x, defect[j].y,defect[j].z)
    Ere = gl.get_value(material + '.' + 'Ere')
    if defect[j].defect_type + '+Int' in list(Ere.keys()):
        interface[k].absorb(defect[j])
    gl.set_value('interface', interface)

    # Clear reactant in defect_mesh
    j0 = index(j)[0]
    j1 = index(j)[1]
    del defect_mesh[j0][j1]
    gl.set_value('defect_mesh', defect_mesh)

    # Clear reactant in migration
    rj = Rmindex(idj-1)
    del Rm[rj]
    for i in range(rj, len(Rm)):
        Rm[i][1] -= 1
    gl.set_value('Rm', Rm)

    # Clear reactant recombination rate and absorption rate
    clearecomb(idj-1)
    cleabsorb(idj-1)

    pass