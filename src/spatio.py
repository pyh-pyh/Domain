import globalvar as gl


def mesh(obj):
    '''Divide defects into little areas'''
    bound = gl.get_value('bound')
    lattice_size = gl.get_value('lattice size')
    defect_mesh = gl.get_value('defect_mesh')
    
    # Scale of the mesh
    lx = int(bound[1]/lattice_size)
    ly = int(bound[3]/lattice_size)
    
    # Identifier of each small area
    n = int(lx * ly * (obj.z // lattice_size) + lx * (obj.y // lattice_size) + obj.x // lattice_size)
    
    # Put neighbor defects together
    defect_mesh[n].append(obj)
    gl.set_value('defect_mesh', defect_mesh)
    
    pass


def index(j):
    '''Put in serial in list defect, return serial in list defect_mesh'''
    bound = gl.get_value('bound')
    lattice_size = gl.get_value('lattice size')
    defect = gl.get_value('defect')
    defect_mesh = gl.get_value('defect_mesh')
    
    # Scale of the mesh
    lx = int(bound[1]/lattice_size)
    ly = int(bound[3]/lattice_size)
    
    # Identifier of each small area
    n = int(lx * ly * (defect[j].z // lattice_size) + lx * (defect[j].y // lattice_size) + defect[j].x // lattice_size)
    
    # Find out serial in defect_mesh[n]
    for i in range(len(defect_mesh[n])):
        if defect_mesh[n][i].ID == defect[j].ID:
            m = i
            break
    
    return (n, m)


def interindex(pos, x, y, z):
    '''Find interface's ID by mesh'''
    interlist = gl.get_value('interlist')
    try:
        ID = interlist.index([pos, x, y, z])
        return ID
    except ValueError:
        return None


def searchmaterial(x, y, z):
    '''Return one lattice's material'''
    lattice = gl.get_value('lattice')
    lattice_size = gl.get_value('lattice size')
    materialist = gl.get_value('materialist')
    cx = int(x // lattice_size)
    cy = int(y // lattice_size)
    cz = int(z // lattice_size)
    code = lattice[cz][cy][cx]
    material = materialist[code-1]
    
    return material


def search(obj):
    '''For neighborhood search'''
    # Find out the position information
    bound = gl.get_value('bound')
    lattice_size = gl.get_value('lattice size')
    defect_mesh = gl.get_value('defect_mesh')
    interface = gl.get_value('interface')
    lx = int(bound[1]/lattice_size)
    ly = int(bound[3]/lattice_size)
    lz = int(bound[5]/lattice_size)
    j = updateID(obj.ID)
    n = index(j)[0]
    cz = n // (lx * ly)
    cy = (n - cz * lx *ly) // lx
    cx = (n - cz * lx *ly) % lx

    # List of all neighbor defects
    roommate = defect_mesh[n]

    neighsur = defect_mesh[lx*ly*cz + lx*cy + (cx+1)%lx] + defect_mesh[lx*ly*cz + lx*cy + (cx-1)%lx] + \
               defect_mesh[lx*ly*cz + lx*((cy+1)%ly) + cx] + defect_mesh[lx*ly*cz + lx*((cy-1)%ly) + cx] + \
               defect_mesh[lx*ly*((cz+1)%lz) + lx*cy + cx] + defect_mesh[lx*ly*((cz-1)%lz) + lx*cy + cx]

    neighedg = defect_mesh[lx*ly*cz + lx*((cy+1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*cz + lx*((cy+1)%ly) + (cx-1)%lx] + \
               defect_mesh[lx*ly*cz + lx*((cy-1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*cz + lx*((cy-1)%ly) + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz+1)%lz) + lx*cy + (cx+1)%lx] + defect_mesh[lx*ly*((cz+1)%lz) + lx*cy + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz-1)%lz) + lx*cy + (cx+1)%lx] + defect_mesh[lx*ly*((cz-1)%lz) + lx*cy + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy+1)%ly) + cx] + defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy-1)%ly) + cx] + \
               defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy+1)%ly) + cx] + defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy-1)%ly) + cx]

    neighcor = defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy+1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy+1)%ly) + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy-1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*((cz+1)%lz) + lx*((cy-1)%ly) + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy+1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy+1)%ly) + (cx-1)%lx] + \
               defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy-1)%ly) + (cx+1)%lx] + defect_mesh[lx*ly*((cz-1)%lz) + lx*((cy-1)%ly) + (cx-1)%lx]

    neighbor = roommate + neighsur + neighedg + neighcor

    # Search for defects that are close to each other
    close = []
    for i in range(len(neighbor)):
        distancesq = (obj.x - neighbor[i].x) ** 2 + (obj.y - neighbor[i].y) ** 2 + (obj.z - neighbor[i].z) ** 2
        if (distancesq <= obj.l ** 2) and (distancesq != 0):
            close.append(neighbor[i])
    
    closeinter = []
    if interindex('x', cx, cy, cz) != None:
        closeinter.append(interface[interindex('x', cx, cy, cz)])
    if interindex('x', (cx+1)%lx, cy, cz) != None:
        closeinter.append(interface[interindex('x', (cx+1)%lx, cy, cz)])
    if interindex('y', cx, cy, cz) != None:
        closeinter.append(interface[interindex('y', cx, cy, cz)])
    if interindex('y', cx, (cy+1)%ly, cz) != None:
        closeinter.append(interface[interindex('y', cx, (cy+1)%ly, cz)])
    if interindex('z', cx, cy, cz) != None:
        closeinter.append(interface[interindex('z', cx, cy, cz)])
    if interindex('z', cx, cy, (cz+1)%lz) != None:
        closeinter.append(interface[interindex('z', cx, cy, (cz+1)%lz)])
    
    return [close, closeinter]


def updateID(idefect):
    '''Update object's ID after some defects removed in list defect'''
    defect = gl.get_value('defect')
    for n in range(len(defect)):
        if defect[n].ID == idefect:
            i = n
            break
    
    return i


def Rmindex(j):
    '''Enter order in list defect, return list in Rm'''
    Rm = gl.get_value('Rm')
    for i in range(len(Rm)):
        if Rm[i][2] == j:
            n = i
            break
    try:
        return n
    except UnboundLocalError:
        return None
