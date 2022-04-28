import pyodbc
#from datetime import date, datetime, timedelta
import cryptocode
import pandas as pd
import configparser
import logging


def cria_relat(cribs, ontem, anteontem):
    config = configparser.ConfigParser()
    config.read('config.ini')
    server = config.get('dados_banco', 'server')
    port = config.get('dados_banco', 'port')
    database = config.get('dados_banco', 'database')
    uid = config.get('dados_banco', 'uid')
    pwd = config.get('dados_banco', 'pwd')

    logging.basicConfig(filename='logFile_relat.log',  level=logging.DEBUG, filemode='w+',
                        format='%(asctime)s - %(levelname)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')

    def conect_db(server, port, database, uid, pwd):
        uid = cryptocode.decrypt(uid, "i9brgroup")
        pwd = cryptocode.decrypt(pwd, "i9brgroup")
        try:
            cnxn = pyodbc.connect(
                f'DRIVER=SQL Server;SERVER={server};PORT={port};DATABASE={database};UID={uid};PWD={pwd};')
            cursor = cnxn.cursor()
            logging.info('conexão com o banco de dados efetuada com sucesso.')
            return cursor, cnxn
        except:
            logging.error('não foi possivel conectar ao banco de dados')


    def select_nodrops(cursor, cribs, ontem, anteontem):


        def select_trans_nodrop(eventdate, anteontem, employee, cribin, cursor): #seleciona todas as transações especificadas no nodrop
            try:
                cursor.execute(f"select transnumber, crib, bin, item, employee, Transdate, quantity, TypeDescription "
                           f"from Trans where employee = '{employee}' and TypeDescription = 'ISSUE' and CribBin = '{cribin}' and transdate >= CONVERT(datetime, '{anteontem}T00:00:00') and Status IS NULL")
                transacoes = cursor.fetchall()
                list_trans_nodrop = []


                for trans in transacoes:
                    #print(trans)
                    transnumber = trans[0]
                    crib = trans[1]
                    bin = trans[2]
                    item = trans[3]
                    employee_trans = trans[4]
                    transdate = trans[5]
                    transdate_limpo = transdate.strftime('%Y-%m-%d')
                    quantity = trans[6]
                    typedesc = trans[7]

                    if transdate_limpo == eventdate:
                        list_trans_nodrop.append(
                            f'{transnumber}, {crib}, {bin}, {item}, {employee_trans}, {transdate}, {quantity}, {typedesc},NAO QUEDA')
                        return list_trans_nodrop[0]

                if len(list_trans_nodrop) == 0:
                    for trans in transacoes:
                        transnumber = trans[0]
                        crib = trans[1]
                        bin = trans[2]
                        item = trans[3]
                        employee_trans = trans[4]
                        transdate = trans[5]
                        transdate_limpo = transdate.strftime('%Y-%m-%d')
                        quantity = trans[6]
                        typedesc = trans[7]
                        if transdate_limpo == anteontem:
                            list_trans_nodrop.append(
                                f'{transnumber}, {crib}, {bin}, {item}, {employee_trans}, {transdate}, {quantity}, {typedesc},NAO QUEDA')
                            return list_trans_nodrop[0]
                logging.info('transações de nodrop selecionadas com sucesso.')
            except:
                logging.warning('Não foi possivel selecionar as transações de nodrop')


        try:
            cursor.execute(f"select EventLogDate, EventLogMessage from EventLog where EventLogKey is null and EventLogProgramName = 'CribMaster' and EventLogDate BETWEEN CONVERT(datetime, '{ontem}T00:00:00') AND CONVERT(datetime, '{ontem}T23:59:59');")
            nodrops = cursor.fetchall()
            list_eventlog = []
            dict_nodrops = {}


            for i in nodrops:
                msg = i[1].split(' ')
                if msg[0] == 'No' and msg[1] == 'Drop' and msg[2] == 'detected':
                    employee = msg[8]
                    cribin = msg[-1]
                    crib = cribin.split('-')
                    crib = int(crib[0])
                    eventlogdate = i[0].strftime('%Y-%m-%d')
                        #print(ontem, anteontem, employee, cribin, cursor)
                    if crib in cribs:
                        if eventlogdate == ontem:
                            list_eventlog.append([employee, cribin, crib, eventlogdate])
                            trans = select_trans_nodrop(ontem, anteontem, employee, cribin, cursor)#chama a função que retornara a transação.
                            #print(trans)
                            if trans is not None:
                                trans = trans.split(',')
                                transnumber = trans[0].replace("'", '')
                                crib = trans[1].replace(' ', '')
                                bin = trans[2].replace(' ', '')
                                item = trans[3].replace(' ', '')
                                employee = trans[4].replace(' ', '')
                                Transdate = trans[5]
                                quantity = trans[6].replace(' ', '')
                                TypeDescription = trans[7].replace(' ', '')
                                type_trans = trans[8]
                                dict_nodrops[transnumber] = [str(crib), bin, item, employee, str(Transdate), str(quantity), TypeDescription, type_trans]



            logging.info('Seleção de nodrops efetuada com sucesso.')

            if dict_nodrops != None and list_eventlog != None:
                return dict_nodrops, list_eventlog
            else:
                return 0,0

        except:
            logging.warning('não foi possivel efetuar o select nos nodrops')


    cursor, cnxx = conect_db(server, port, database, uid, pwd)

    dict_nodrops, list_eventlog = select_nodrops(cursor, cribs, ontem, anteontem)
    #select_nodrops(cursor, cribs, ontem, anteontem)
    print(dict_nodrops)
    print(list_eventlog)
    print(len(list_eventlog))

    '''funcionando, agora precisa trabalhar no cancelamento'''