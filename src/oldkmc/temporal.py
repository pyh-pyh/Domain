import time
import globalvar as gl

def timanager(t, tstart, init = 'no'):
    '''Track and record time'''
    if init == 'yes':
        timelist = []
        timelist.append([t, time.time() - tstart])
        gl.set_value('timanager', timelist)
    if init == 'no':
        timelist = gl.get_value('timanager')
        timelist.append([t, time.time() - tstart])
        gl.set_value('timanager', timelist)

    pass