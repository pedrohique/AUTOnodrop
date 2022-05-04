import pandas as pd
from datetime import datetime, date


def Create_New_Trans(dados, pasta_prontos, pasta_crib, data):
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
        Transdate = '02/05/2022'
        Transtime = '13:27'
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


def Update_trans(dados, pasta_prontos, pasta_crib, data):
    new_data = {'transnumber': [], 'Status':[]}
    for key in dados.keys():
        transnumber = key
        status = 1
        new_data['transnumber'].append(transnumber)
        new_data['Status'].append(status)
    df = pd.DataFrame.from_dict(new_data)

    df.to_csv(pasta_prontos + f'updatetrans-{data}.csv', index=False)
    df.to_csv(pasta_crib + f'updatetrans-{data}.csv', index=False)

def Update_station(dados, pasta_prontos, pasta_crib, data):
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

def Cria_Arquivos(dados, pasta_prontos, pasta_crib):
    data = date.today()
    Create_New_Trans(dados, pasta_prontos, pasta_crib, data)
    Update_trans(dados, pasta_prontos, pasta_crib, data)
    Update_station(dados, pasta_prontos, pasta_crib, data)