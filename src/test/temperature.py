import globalvar as gl


def initemperature(temp):
    '''Initialize temperature'''
    gl.set_value('temperature', temp)

    pass


def functrans(function):
    '''Transform the customized function into mathematical expression'''
    gap = []
    formula = []
    funcgroup = function.split(';')
    for i in range(len(funcgroup)):
        funcgroup[i] = funcgroup[i].split(':')
        for j in range(len(funcgroup[i][0])):
            if funcgroup[i][0][j] == ',':
                gap.append(float(funcgroup[i][0][j+1:len(funcgroup[i][0])-1]))
                formula.append(funcgroup[i][1])
    
    return [gap, formula]


def getemperature(t):
    '''Define temperature mode'''
    tempmode = gl.get_value('tempmode')
    initemp = tempmode[0]
    mode = tempmode[1]
    slope = tempmode[2]
    function = tempmode[3]
    if mode == 'constant':
        pass
    
    elif mode == 'uniform':
        temp = initemp + slope * t
        gl.set_value('temperature', temp)
    
    elif mode == 'selfdefine':
        formulaset = functrans(function)
        for i in range(len(formulaset[0])):
            if t <= formulaset[0][i]:
                temp = eval(formulaset[1][i])
                break
        gl.set_value('temperature', temp)
    
    pass

