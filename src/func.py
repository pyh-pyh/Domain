import time
import numpy as np
import globalvar as gl
from numba import jit
from defect import ED, MP
from event import break_up, franck_turnbull, migrate, recombine, absorb
from globalvar import initial
from output import lmpoutput, numoutput, timeoutput
from simulation import idmanager, recomblist, searchint
from spatio import mesh, updateID, searchmaterial
from temporal import timanager
from temperature import getemperature, initemperature


@jit
def set_temperature(initemp, mode = 'constant', slope = 0, function = '3*t^2+1'):
    '''Set temperature'''
    initemperature(initemp)
    gl.set_value('tempmode', [initemp, mode, slope, function])

    pass

@jit
def set_output(style, mode, interval):
    '''Set output'''
    if style == 'distribution':
        gl.set_value('lmpoutput', True)
        gl.set_value('lmpmode', mode)
        gl.set_value('lmpinterval', interval)
    if style == 'count':
        gl.set_value('numoutput', True)
        gl.set_value('numode', mode)
        gl.set_value('numinterval', interval)

    pass

@jit
def get_defect_data(filename, unitconvert = 1):
    '''Import data of defect, return a list of defect objects'''
    # Read and split the data from text
    with open('data/' + filename) as f:
        N = int(f.readline())
        lines = f.readlines()
    gl.set_value('defectdata', [lines[i].strip().split() for i in range(N)])

    # Generate defect objects and put them in a list
    defect = []
    defectype = gl.get_value('defectype')
    defectdata = gl.get_value('defectdata')
    for i in range(N):
        if defectdata[i][1] in defectype['MP']:
            a = MP(ID = int(defectdata[i][0]), defect_type = defectdata[i][1], 
            x = float(defectdata[i][2])*unitconvert, y = float(defectdata[i][3])*unitconvert, z = float(defectdata[i][4])*unitconvert)
            defect.append(a)
        elif defectdata[i][1] in defectype['ED']:
            a = ED(ID = int(defectdata[i][0]), defect_type = defectdata[i][1], 
            x = float(defectdata[i][2])*unitconvert, y = float(defectdata[i][3])*unitconvert, z = float(defectdata[i][4])*unitconvert)
            defect.append(a)
    gl.set_value('defect', defect)

    pass

@jit
def generate_defect_data(N, defectype = ['I', 'V']):
    '''If no exsiting data file, generate one randomly'''
    with open('data/generate.txt','w') as f:
        bound = gl.get_value('bound')
        print(N, file = f)
        for i in range(N):
            flag = np.random.randint(len(defectype))
            x = np.random.random_sample()
            y = np.random.random_sample()
            z = np.random.random_sample()
            print('%d %s %f %f %f'%(i+1, defectype[flag], x*bound[1], y*bound[3], z*bound[5]), file = f)
    get_defect_data('generate.txt')

    pass

@jit
def read_config(filename, defectype):
    '''Read one material's configure'''
    with open('config/' + filename + '/' + defectype + '.txt', 'r') as f:
        config = f.readlines()
        i = 0
        while i+1 < len(config):
            # Read prefactor
            if config[i].strip() == 'prefactor':
                v0 = float(config[i+1])
                gl.set_value(filename + '.' + defectype + '.v0', v0)
                i += 1
                continue
            
            # Read migration distance
            elif config[i].strip() == 'migration distance':
                lmig = {}
                while i+1 < len(config):
                    if config[i+1] != '\n':
                        lmig[config[i+1].split()[0]] = float(config[i+1].split()[1])
                        i += 1
                    else:
                        break
                gl.set_value(filename + '.' + defectype + '.lmig', lmig)
                continue
            
            # Read migrate rate data
            elif config[i].strip() == 'Em':
                Em = {}
                while i+1 < len(config):
                    if config[i+1] != '\n':
                        Em[config[i+1].split()[0]] = float(config[i+1].split()[1])
                        i += 1
                    else:
                        break
                gl.set_value(filename + '.' + defectype + '.Em', Em)
                continue
            
            # Read break-up rate data
            elif config[i].strip() == 'Ebk':
                Ebk = {}
                while i+1 < len(config):
                    if config[i+1] != '\n':
                        Ebk[config[i+1].split()[0]] = float(config[i+1].split()[1])
                        i += 1
                    else:
                        break
                gl.set_value(filename + '.' + defectype + '.Ebk', Ebk)
                continue
            
            # Read F-T rate data
            elif config[i].strip() == 'Eft':
                Eft = {}
                while i+1 < len(config):
                    if config[i+1] != '\n':
                        Eft[config[i+1].split()[0]] = float(config[i+1].split()[1])
                        i += 1
                    else:
                        break
                gl.set_value(filename + '.' + defectype + '.Eft', Eft)
                continue

            i += 1

    pass

@jit
def read_reaction(filename):
    '''Read defined reactions in one material'''
    with open('config/' + filename + '/Reaction.txt', 'r') as f:
        reaction = f.readlines()
        i = 0
        Ere = {}
        while i < len(reaction):
            if reaction[i] != '\n':
                Ere[reaction[i].split()[0]] = [reaction[i].split()[1], float(reaction[i].split()[2])]
                i += 1
            else:
                break
        gl.set_value(filename + '.' + 'Ere', Ere)

    pass

@jit
def read_box():
    '''Read simulation box properties'''
    with open('config/Box.txt', 'r') as f:
        box = f.readlines()
        i = 0
        while i < len(box):
            if box[i].strip() == 'box size':
                gl.set_value('bound', [float(box[i+1].split()[1]),float(box[i+1].split()[2]),\
                                       float(box[i+2].split()[1]),float(box[i+2].split()[2]),\
                                       float(box[i+3].split()[1]),float(box[i+3].split()[2])])
                i += 3
                continue
            
            elif box[i].strip() == 'lattice size':
                gl.set_value('lattice size', float(box[i+1].strip()))
                i += 1
                continue

            elif box[i].strip() == 'material':
                material = []
                while i+1 < len(box):
                    if box[i+1] != '\n':
                        material.append(box[i+1].split()[1])
                        i += 1
                    else:
                        break
                gl.set_value('materialist', material)
                continue

            elif box[i].strip() == 'defect type':
                defectlist = {}
                while i+1 < len(box):
                    if box[i+1] != '\n':
                        defectlist[box[i+1].split()[0]] = box[i+1].split()[1:]
                        i += 1
                    else:
                        break
                gl.set_value('defectype', defectlist)
                continue
            
            elif box[i].strip() == 'distribution':
                lattice = []
                panel = []
                z = 0
                while i+1 < len(box):
                    if box[i+1] != '\n':
                        if box[i+1].strip() != 'z = ' + str(z):
                            strip = [int(box[i+1].split()[j]) for j in range(len(box[i+1].split()))]
                            panel.append(strip)
                            i += 1
                        else:
                            i += 1
                            if z != 0:
                                lattice.append(panel)
                            z += 1
                            panel = []
                    else:
                        break
                lattice.append(panel)
                gl.set_value('lattice', lattice)
                continue
            
            i += 1

    pass

@jit
def load_material():
    '''Load parameters of one particular material'''
    read_box()
    material = gl.get_value('materialist')
    for i in range(len(material)):
        read_config(material[i], 'MP')
        read_config(material[i], 'ED')
        read_reaction(material[i])
    
    pass

@jit
def run_simulation(simulation_time):
    '''Simulation body'''
    
    # Variates define during the loop
    t = 0
    count = 0
    mig = 0
    brk = 0
    FT = 0
    re = 0
    ab = 0
    init = 0
    tstart = time.time()
    gl.set_value('simulation time', simulation_time)
    timanager(t, tstart, init = 'yes')
    defect = gl.get_value('defect')
    defectype = gl.get_value('defectype')
    temperature = gl.get_value('temperature')
    
    # Clear text data
    f = open('data/output.txt','w')
    f.truncate()
    f.close()
    f = open('data/result.txt','w')
    f.truncate()
    title = ['time'] + defectype['MP'] + defectype['ED'] + ['temperature']
    print(*title, file = f)
    f.close()
    f = open('data/time.txt','w')
    f.truncate()
    f.close()

    # Initialize ID manager
    idmanager(initial = 'yes')
    
    # Generate mesh of initial defects
    # Notice that if bound too small, dividing area may cause scale of little area similar to the capture distance!!! NEED FURTHER FIXING!!!
    bound = gl.get_value('bound')
    lattice_size = gl.get_value('lattice size')
    lx = int(bound[1]/lattice_size)
    ly = int(bound[3]/lattice_size)
    lz = int(bound[5]/lattice_size)
    gl.set_value('defect_mesh', [[] for i in range(lx*ly*lz)])
    for i in range(len(defect)):
        mesh(defect[i])
    searchint()
    interface = gl.get_value('interface')

    # Generate recombination rate table of initial defects
    gl.set_value('Rre', [])
    gl.set_value('Rint', [])
    for i in range(len(defect)):
        recomblist(defect[i])
    #checkrepeat()
    Rre = gl.get_value('Rre')
    Rint = gl.get_value('Rint')

    # Begin of the loop
    while t <= simulation_time:
        
        # Get temperature
        getemperature(t)
        temperature = gl.get_value('temperature')

        # Check list defect_mesh
        '''a = 0
        for i in range(1000):
            print(len(defect_mesh[i]))
            a += len(defect_mesh[i])
        print(a)'''

        # Collect rates
        if init == 0:
            Rm = [[defect[i].rate(temperature)[0], i, i] for i in range(len(defect)) if defect[i].rate(temperature)[0] != 0]
            #print('Rm', len(Rm))
            Rbk = [[defect[i].rate(temperature)[1], i] for i in range(len(defect)) if defect[i].rate(temperature)[1] != 0]
            #print('Rbk', len(Rbk))
            Rft = [[defect[i].rate(temperature)[2], i] for i in range(len(defect)) if defect[i].rate(temperature)[2] != 0]
            #print('Rft', len(Rft))
            RN = [Rm[i][0] for i in range(len(Rm))] + [Rbk[i][0] for i in range(len(Rbk))] + \
             [Rft[i][0] for i in range(len(Rft))] + [Rre[i][0] for i in range(len(Rre))] + \
             [Rint[i][0] for i in range(len(Rint))]
            gl.set_value('Rm', Rm)
            gl.set_value('Rbk', Rbk)
            gl.set_value('Rft', Rft)
            gl.set_value('RN', RN)
            init = 1
        else:
            Rm = gl.get_value('Rm')
            Rbk = gl.get_value('Rbk')
            Rft = gl.get_value('Rft')
            RN = [Rm[i][0] for i in range(len(Rm))] + [Rbk[i][0] for i in range(len(Rbk))] + \
             [Rft[i][0] for i in range(len(Rft))] + [Rre[i][0] for i in range(len(Rre))] + \
             [Rint[i][0] for i in range(len(Rint))]
            gl.set_value('Rm', Rm)
            gl.set_value('Rbk', Rbk)
            gl.set_value('Rft', Rft)
            gl.set_value('RN', RN)
        #print('RN', len(RN))
        #print('Rre', len(Rre))

        # Generate two random numbers
        s = np.random.random_sample()
        r = np.random.random_sample()
        #print('r*RN', r * sum(RN))

        # The upper and lower bound of the binary tree
        point = len(RN)//2
        #print('point', point)
        up = len(RN)
        down = 0

        while True:
            
            # Fall in the period
            if (sum(RN[:point]) <= r * sum(RN)) and (sum(RN[:(point+1)%(len(RN)+1)]) > r * sum(RN)):
                count += 1
                '''print('find', point, sum(RN[:point]), sum(RN[:(point+1)%(len(RN)+1)]), r * sum(RN))
                print(count)'''

                # Judge which kind of event happens
                if point < len(Rm):
                    j = Rm[point][2] + 1
                    idj = updateID(j)
                    print('defect %d %s migrate'%(defect[idj].ID, defect[idj].defect_type), (defect[idj].x, defect[idj].y, defect[idj].z), t)
                    mig += 1
                    migrate(point)

                elif (point >= len(Rm)) and (point < len(Rm) + len(Rbk)):
                    j = Rbk[point - len(Rm)][1]
                    print('defect %d %s break up'%(defect[j].ID, defect[j].defect_type), (defect[j].x, defect[j].y, defect[j].z), t)
                    brk += 1
                    break_up(point)

                elif (point >= len(Rm) + len(Rbk)) and (point < len(Rm) + len(Rbk) + len(Rft)):
                    j = Rft[point - len(Rbk) - len(Rm)][1]
                    print('defect %d %s F-T'%(defect[j].ID, defect[j].defect_type), (defect[j].x, defect[j].y, defect[j].z), t)
                    FT += 1
                    franck_turnbull(point)
                
                elif point >= len(Rm) + len(Rbk) + len(Rft) and (point < len(Rm) + len(Rbk) + len(Rft) + len(Rre)):
                    idj = Rre[point - len(Rbk) - len(Rm) - len(Rft)][1] + 1
                    idk = Rre[point - len(Rbk) - len(Rm) - len(Rft)][2] + 1
                    j = updateID(idj)
                    k = updateID(idk)
                    print('defect %d %s, %d %s recombine'%(defect[j].ID, defect[j].defect_type, defect[k].ID, defect[k].defect_type), 
                    (defect[j].x, defect[j].y, defect[j].z), (defect[k].x, defect[k].y, defect[k].z), t)
                    re += 1
                    recombine(point)

                elif point >= len(Rm) + len(Rbk) + len(Rft) + len(Rre):
                    idj = Rint[point - len(Rbk) - len(Rm) - len(Rft) - len(Rre)][1] + 1
                    j = updateID(idj)
                    k = Rint[point - len(Rbk) - len(Rm) - len(Rft) - len(Rre)][2]
                    print('defect %d %s absorbed by interface %d %s'%(defect[j].ID, defect[j].defect_type, interface[k].ID, interface[k].defect_type), 
                    (defect[j].x, defect[j].y, defect[j].z), (interface[k].x, interface[k].y, interface[k].z), t)
                    ab += 1
                    absorb(point)

                # Accelerate time
                dt = -np.log(s)/sum(RN)
                t += dt
                timanager(t, tstart)

                # Text output
                lop = gl.get_value('lmpoutput')
                nop = gl.get_value('numoutput')
                if lop:
                    lmpoutput(count, t)
                if nop:
                    numoutput(count, t)
                break

            # Too big
            if sum(RN[:point]) > r * sum(RN):
                #print('big', point, sum(RN[:point]), r * sum(RN))
                up = point
                point = int((up + down)/2)
                continue

            # Too small
            if sum(RN[:(point+1)%(len(RN)+1)]) < r * sum(RN):
                #print('small', point, sum(RN[:(point+1)%len(RN)]), r * sum(RN))
                down = point
                point = int((up + down)/2)
                continue

    tend = time.time()
    timeoutput()
    print('global variable =', list(gl._global_dict.keys()))
    print('run time =', tend - tstart)
    print('event =', count)
    print('migration =', mig)
    print('break up =', brk)
    print('Franck-Turnbull =', FT)
    print('recombine =', re)
    print('absorb =', ab)
    
    pass
