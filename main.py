from corpo import find_nodrop

ontem = '2022-04-28'
anteontem = '2022-04-27'

cribs_range = range(1,300)
cribs = []
for i in cribs_range:
    cribs.append(i)
    #print(i)

#print(cribs)
find_nodrop.cria_relat(cribs, ontem, anteontem)