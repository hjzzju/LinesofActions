legal_moves = []
row = ['0','1','2','3','4','5','6','7'] #row of the board
col = ['0','1','2','3','4','5','6','7'] #col of the board
for i in range(8):
    for j in range(8):
        des = [(i + t, j) for t in range(-8, 9)] + [(i, j + t) for t in range(-8, 9)] + [(i + t, j + t) for t in range(-8, 9)] + [(i - t, j + t) for t in range(-8, 9)]
        for (nex_i, nex_j) in des:
            if nex_i in range(0, 8) and nex_j in range(0, 8) and (i != nex_i or j != nex_j):
                legal_moves.append(row[i] + col[j] + row[nex_i] + col[nex_j])
# print(len(legal_moves))
# print(legal_moves)
#
# print(legal_moves.index())

# a = [0,1]
# b = [0.5,0.5]
#
# c = zip(a,b)
#
# ac,bc = zip(*c)
# print(bc)
legal_map = {}
for i, move in enumerate(legal_moves):
    legal_map[move] = i

print(legal_map)

