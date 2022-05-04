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


nome_arquivo_pronto = config.get('funcionamento', 'nome_arquivo_pronto')
pasta_prontos = ''#config.get('funcionamento', 'pasta_prontos') + '\\' + nome_arquivo_pronto
pasta_crib = ''#config.get('funcionamento', 'pasta_crib') + '\\' + nome_arquivo_pronto

cribs = config.get('funcionamento', 'cribs').replace(' ', '').split(',')
cribs = list(map(int, cribs))


print(pasta_prontos)
print(pasta_crib)
print(nome_arquivo_pronto)


ontem = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
anteontem = (datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')


dados = find_nodrop.cria_relat(cribs, ontem, anteontem)

Create_files.Cria_Arquivos(dados, pasta_prontos, pasta_crib)

'''sistema pronto iniciar testes em homolog com relatorio de emails desativados, verificar cm edilson a criação de uma base nova para rodar os dois em paralelo'''
# while True:
#
#     horario = datetime.today().strftime('%H:%M')
#     data = datetime.today().strftime('%d-%m-%y-%H-%M')
#     if horario in horarios:
#
#         ontem = (datetime.today()- timedelta(days=1)).strftime('%Y-%m-%d')
#         anteontem = (datetime.today()- timedelta(days=2)).strftime('%Y-%m-%d')
#
#         dados = find_nodrop.cria_relat(cribs, ontem, anteontem)
#
#         Create_files.Cria_Arquivos(dados, pasta_prontos, pasta_crib)
