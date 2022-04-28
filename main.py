from corpo import find_nodrop

ontem = '2022-04-26'
anteontem = '2022-04-26'

cribs_range = range(1,150)
cribs = []
for i in cribs_range:
    cribs.append(i)
    #print(i)

#print(cribs)
find_nodrop.cria_relat(cribs, ontem, anteontem)