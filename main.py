from corpo import find_nodrop
from corpo import Create_files
from datetime import datetime, date, timedelta
import logging
import configparser


def horario_prox(list_horarios, horario):
    list_dif = []
    horario = datetime.strptime(horario, '%H:%M').time()

    for i in list_horarios:
        hora_obj = datetime.strptime(i, '%H:%M').time()
        falta = (datetime.combine(date.min, hora_obj) - datetime.combine(date.min, horario)) / timedelta(
            seconds=1)
        dia = timedelta(days=1) / timedelta(seconds=1)
        if falta < 0:
            falta = dia - (falta * -1)
        falta = int(falta)
        list_dif.append(falta)

    return min(list_dif), list_dif.index(min(list_dif))

config = configparser.ConfigParser()
config.read('config.ini')


horarios = config.get('funcionamento', 'horarios').replace(' ', '').split(',')
pasta = config.get('funcionamento', 'pasta')
pasta_prontos = config.get('funcionamento', 'pasta_prontos')
pasta_crib = config.get('funcionamento', 'pasta_crib')


ontem = '2022-04-29'
anteontem = '2022-04-28'

cribs_range = range(1,300)
cribs = [171, 150, 151, 152, 153, 154, 170, 130, 200, 201, 202, 203, 204, 205]

nodrops = find_nodrop.cria_relat(cribs, ontem, anteontem)
Create_files.Create_New_Trans(nodrops)
Create_files.Update_trans(nodrops)
Create_files.Update_station(nodrops)

# while True:
#
#     horario = datetime.today().strftime('%H:%M')
#     data = datetime.today().strftime('%d-%m-%y-%H-%M')
#     if horario in horarios:
#         ontem = '2022-04-29'
#         anteontem = '2022-04-28'
#
#         cribs_range = range(1,300)
#         cribs = [171, 150, 151, 152, 153, 154, 170, 130, 200, 201, 202, 203, 204, 205]
#
#         nodrops = find_nodrop.cria_relat(cribs, ontem, anteontem)
#         Create_files.Create_New_Trans(nodrops)
#         Create_files.Update_trans(nodrops)
#         Create_files.Update_station(nodrops)
#         #print(nodrops)