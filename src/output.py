import globalvar as gl
import numpy as np


def lmprint(t):
    '''Print data'''
    defect = gl.get_value('defect')
    bound = gl.get_value('bound')
    defectype = gl.get_value('defectype')
    defectlist = defectype['MP'] + defectype['ED']
    order = {}
    with open('data/output.txt','a') as output:
        print('ITEM: TIMESTEP', file=output)
        print(t, file=output)
        print('ITEM: NUMBER OF ATOMS', file=output)
        print(len(defect), file=output)
        print('ITEM: BOX BOUNDS', file=output)
        print('%5.2f %5.2f\n%5.2f %5.2f\n%5.2f %5.2f'%(bound[0], bound[1], bound[2], bound[3], bound[4], bound[5]), file=output)
        print('ITEM: ATOMS id type x y z', file=output)
        for i in range(len(defectlist)):
            order[defectlist[i]] = (i+1) * 20
        for i in range(len(defect)):
            temtype = order[defect[i].defect_type]
            print('%d   %d  %f  %f  %f'%(i+1,temtype,defect[i].x,defect[i].y,defect[i].z), file = output)

    pass


def lmpoutput(count, t):
    '''Data output in LAMMPS form'''
    mode = gl.get_value('lmpmode')
    interval = gl.get_value('lmpinterval')
    if mode == 'MCsteps':
        if count % interval == 0:
            lmprint(t)
    if mode == 'time uniform':
        divide = gl.get_value('lmp time uniform divide')
        if divide == None:
            divide = 0
        if divide == t // interval:
            pass
        if divide != t // interval:
            for i in range(int(t // interval - divide)):
                lmprint(t + i * interval)
            gl.set_value('lmp time uniform divide', t // interval)
    if mode == 'time log':
        if gl.get_value('lmp time log list') == None:
            time = gl.get_value('simulation time')
            dtlog = np.log10(time + 1)/interval
            logt = []
            for i in range(interval):
                logt.append(10 ** (i*dtlog) - 1)
            logt.append(time)
            gl.set_value('lmp time log list', logt)
        else:
            logt = gl.get_value('lmp time log list')
            if logt == []:
                pass
            if t < logt[0]:
                pass
            if t >= logt[0]:
                lmprint(t)
                del logt[0]
                gl.set_value('lmp time log list', logt)
    
    pass


def numprint(t):
    '''Print data'''
    number = gl.get_value('number')
    defect = gl.get_value('defect')
    for i in range(len(defect)):
        number[defect[i].defect_type] += 1
    with open('data/result.txt','a') as output:
        print(t, *list(number.values()), gl.get_value('temperature'), file = output)
    gl.set_value('number', number)

    pass


def numoutput(count, t):
    '''Count total number of all defects and output'''
    defectype = gl.get_value('defectype')
    num = {}
    for i in range(len(defectype['MP'])):
        num[defectype['MP'][i]] = 0
    for i in range(len(defectype['ED'])):
        num[defectype['ED'][i]] = 0
    gl.set_value('number', num)
    mode = gl.get_value('numode')
    interval = gl.get_value('numinterval')
    if mode == 'MCsteps':
        if count % interval == 0:
            numprint(t)
    if mode == 'time uniform':
        divide = gl.get_value('num time uniform divide')
        if divide == None:
            divide = 0
        if divide == t // interval:
            pass
        if divide != t // interval:
            numprint(t)
            gl.set_value('num time uniform divide', t // interval)
    if mode == 'time log':
        if gl.get_value('num time log list') == None:
            time = gl.get_value('simulation time')
            dtlog = np.log10(time + 1)/interval
            logt = []
            for i in range(interval):
                logt.append(10 ** (i*dtlog) - 1)
            logt.append(time)
            gl.set_value('num time log list', logt)
        else:
            logt = gl.get_value('num time log list')
            if t < logt[0]:
                pass
            if t >= logt[0]:
                numprint(t)
                del logt[0]
                gl.set_value('num time log list', logt)
    
    pass


def timeoutput():
    '''Output time data'''
    with open('data/time.txt','a') as output:
        for i in range(len(gl.get_value('timanager'))):
            print(i, gl.get_value('timanager')[i][0], gl.get_value('timanager')[i][1], file = output)
    
    pass