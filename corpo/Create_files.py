import pandas as pd
from datetime import datetime, date, timedelta
import logging
import time


def Create_New_Trans(dados, pasta_prontos, pasta_crib, data, data_dados):
    try:
        dados_new = {'station':[], 'bin':[], 'Item':[], 'employee':[], 'User1':[], 'User2':[],  'quantity':[], 'Transdate':[],
                     'Transtime':[],'type':[],'TypeDescription':[],'binqty':[],'RelatedKey':[],'CribBin':[],'IssuedTo':[],
                     'Crib':[],'UsageType':[] }

        for key in dados.keys():
            #print(dados[key])
            station = dados[key][0]
            bin = dados[key][1]
            Item = dados[key][2]
            employee = 'i9007'
            User1 = dados[key][7]
            User2 = dados[key][8]
            quantity = (int(dados[key][5])*-1)
            Transdate = data_dados
            Transtime = '22:22'
            type = 'X'
            TypeDescription = 'CANCL'
            binqty = (int(dados[key][9])+1)
            RelatedKey = key
            CribBin = f'{station}-{bin}'
            IssuedTo = dados[key][3]
            Crib = station
            UsageType = 1

            dados_new['station'].append(station)
            dados_new['bin'].append(bin)
            dados_new['Item'].append(Item)
            dados_new['employee'].append(employee)
            dados_new['User1'].append(User1)
            dados_new['User2'].append(User2)
            dados_new['quantity'].append(quantity)
            dados_new['Transdate'].append(Transdate)
            dados_new['Transtime'].append(Transtime)
            dados_new['type'].append(type)
            dados_new['TypeDescription'].append(TypeDescription)
            dados_new['binqty'].append(binqty)
            dados_new['RelatedKey'].append(RelatedKey)
            dados_new['CribBin'].append(CribBin)
            dados_new['IssuedTo'].append(IssuedTo)
            dados_new['Crib'].append(Crib)
            dados_new['UsageType'].append(UsageType)


        df = pd.DataFrame.from_dict(dados_new)

        df.to_csv(pasta_prontos + f'trans-{data}.csv', index=False)
        df.to_csv(pasta_crib + f'trans-{data}.csv', index=False)
        logging.info('Arquivo de criação de cancl criado sucesso.')

        return True
    except:
        logging.error('Arquivo de criação de Cancl não pode ser criado')
        return False


def Update_trans(dados, pasta_prontos, pasta_crib, data, data_dados):
    try:
        new_data = {'transnumber': [], 'Status':[]}
        for key in dados.keys():
            transnumber = key
            status = 1
            new_data['transnumber'].append(transnumber)
            new_data['Status'].append(status)
        df = pd.DataFrame.from_dict(new_data)

        df.to_csv(pasta_prontos + f'updatetrans-{data}.csv', index=False)
        df.to_csv(pasta_crib + f'updatetrans-{data}.csv', index=False)

        logging.info('Arquivo de Update criado com sucesso.')
        return True
    except:
        logging.error('Não foi possivel criar o arquivo de Update Trans')
        return False

def Update_station(dados, pasta_prontos, pasta_crib, data, data_dados):
    try:
        new_data = {'Cribbin':[], 'quantity':[], 'BinQuantity':[]}
        for key in dados.keys():
            cribbin = f'{dados[key][0]}-{dados[key][1]}'
            quantity = int(dados[key][5])
            binquantity = quantity
            new_data['Cribbin'].append(cribbin)
            new_data['quantity'].append(quantity)
            new_data['BinQuantity'].append(binquantity)
        df = pd.DataFrame.from_dict(new_data)

        df.to_csv(pasta_prontos + f'updatestation-{data}.csv', index=False)
        df.to_csv(pasta_crib + f'updatestation-{data}.csv', index=False)
        logging.info('Arquivo de atualização de estoque criado com sucesso.')
        return True
    except:
        logging.error('Não fi possivel criar o arquivo de atualização de estoque')
        return False

def Cria_Arquivos(dados, pasta_prontos, pasta_crib):
    logging.info('Iniciando a criação dos arquivos de importação')
    data = datetime.today().strftime('%Y%m%d%I%M%S')
    data_dados = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(data_dados)
    resp_cancl = Create_New_Trans(dados, pasta_prontos, pasta_crib, data, data_dados)
    time.sleep(10)
    if resp_cancl == True:
        resp_update = Update_trans(dados, pasta_prontos, pasta_crib, data, data_dados)
        time.sleep(10)
        if resp_update == True:
            resp_statio = Update_station(dados, pasta_prontos, pasta_crib, data, data_dados)

