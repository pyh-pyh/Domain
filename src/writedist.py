L = 20

with open(r'config\Box.txt', 'a') as f:
    for i in range(L):
        print('z =', str(i), file = f)
        for j in range(L):
            for k in range(L):
                print(1, end = ' ', file = f)
            print(end = '\n', file = f)