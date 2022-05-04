import pyodbc
#from datetime import date, datetime, timedelta
import cryptocode
import pandas as pd
import configparser
import logging


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





def select_trans_nodrop(eventdate, anteontem, employee, cribin,
                        cursor):  # seleciona todas as transações especificadas no nodrop
    try:
        cursor.execute(
            f"select transnumber, crib, bin, item, employee, Transdate, quantity, TypeDescription, User1, User2, binqty "
            f"from Trans where employee = '{employee}' and TypeDescription = 'ISSUE' and CribBin = '{cribin}' and transdate >= CONVERT(datetime, '{anteontem}T00:00:00') and Status IS NULL")
        transacoes = cursor.fetchall()
        list_trans_nodrop = []  # lista de transações possiveis para o nodrop vai retornar sempre a primeira ou index 0
        contador = 0

        for trans in transacoes:  # procura as transações no dia de ontem
            transnumber = trans[0]
            crib = trans[1]
            bin = trans[2]
            item = trans[3]
            employee_trans = trans[4]
            transdate = trans[5]
            transdate_limpo = transdate.strftime('%Y-%m-%d')
            quantity = trans[6]
            typedesc = trans[7]
            user1 = trans[8]
            user2 = trans[9]
            binqty = trans[10]
            cribbin = f'{crib}-{bin}'
            contador += contador + 1

            if transdate_limpo == eventdate:
                list_trans_nodrop.append(
                    f'{transnumber}, {crib}, {bin}, {item}, {employee_trans}, {transdate}, {quantity}, {typedesc},{user1}, {user2}, {binqty},NAO QUEDA')
                return list_trans_nodrop[0]

        if len(list_trans_nodrop) == 0:  # Caso não encontre verifica se as transações estão na data de ante ontem
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
                user1 = trans[8]
                user2 = trans[9]
                binqty = trans[10]
                if transdate_limpo == anteontem:
                    list_trans_nodrop.append(
                        f'{transnumber}, {crib}, {bin}, {item}, {employee_trans}, {transdate}, {quantity}, {typedesc},{user1}, {user2}, {binqty},NAO QUEDA')
                    return list_trans_nodrop[0]

        logging.info('transações de nodrop selecionadas com sucesso.')
    except:
        logging.warning('Não foi possivel selecionar as transações de nodrop')


def select_nodrops(cursor, cribs, ontem, anteontem):
        def remove_repetidos(lista):
            l = []
            for i in lista:
                if i not in l:
                    l.append(i)
            l.sort()
            return l


        def count_cancel(cursor, employee, cribin, ontem):
            cursor.execute(
                f"select transnumber, RelatedKey, crib, bin, item, employee, Transdate, quantity, TypeDescription, User1, User2, binqty "
                f"from Trans where issuedto = '{employee}' and TypeDescription = 'CANCL' and CribBin = '{cribin}' and transdate >= CONVERT(datetime, '{ontem}T00:00:00') ")
            transacoes = cursor.fetchall()
            # print(len(transacoes), 'cancelamentos')
            # print(transacoes)
            return len(transacoes)

        try:
            cursor.execute(
                    f"select EventLogDate, EventLogMessage from EventLog where EventLogKey is null and EventLogProgramName = 'CribMaster' and EventLogDate BETWEEN CONVERT(datetime, '{ontem}T00:00:00') AND CONVERT(datetime, '{ontem}T23:59:59');")
            nodrops = cursor.fetchall()
            list_eventlog = []
            dict_nodrops = {}
            soma_nodrops = 0
            soma_cancelamentos = 0

            for i in nodrops:

                #print(i)
                msg = i[1].split(' ')
                if msg[0] == 'No' and msg[1] == 'Drop' and msg[2] == 'detected':
                    employee = msg[8]
                    cribin = msg[-1]
                    crib = cribin.split('-')
                    crib = int(crib[0])
                    eventlogdate = i[0].strftime('%Y-%m-%d')
                    # print(ontem, anteontem, employee, cribin, cursor)
                    # count_cancel(cursor, employee, cribin, anteontem)

                    print(crib)
                    if crib in cribs:
                        print(cribs)
                        if eventlogdate == ontem:
                            list_eventlog.append([employee, cribin, crib, eventlogdate])
                            # print(cribin)

            list_eventlog_base = remove_repetidos(
                list_eventlog)  # remove nodrops repetidos para realizar a contagem a baixo

            for nodrop_unic in list_eventlog_base:
                print('----------------------------------')
                # print(nodrop_unic)
                employee = nodrop_unic[0]
                cribin = nodrop_unic[1]
                crib = nodrop_unic[2]
                eventlogdate = nodrop_unic[3]
                contagem = list_eventlog.count(nodrop_unic)  # conta quantidade de nodrops
                print(contagem, 'nodrop')
                count_cancel_var = count_cancel(cursor, employee, cribin,
                                                ontem)  # conta quantidade de cancelamentos para cada nodrop unico
                print(count_cancel_var, 'cancelamentos')
                soma_cancelamentos += count_cancel_var
                soma_nodrops += contagem
                if contagem > count_cancel_var:
                    '''se a quantidade de nodrops e cancelamentos for que a de cancelamentos não adiciona transação no dicionario'''
                    trans = select_trans_nodrop(ontem, anteontem, employee, cribin,
                                                cursor)  # chama a função que retornara a transação.
                    print(trans)
                    # caso a transação ja tenha sido cancelada manualmente ela vai retornar none
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
                        # type_trans = trans[8]
                        user1 = trans[8].replace(' ', '')
                        user2 = trans[9].replace(' ', '')
                        binqty = trans[10].replace(' ', '')
                        dict_nodrops[transnumber] = [str(crib), bin, item, employee, str(Transdate), str(quantity),
                                                     TypeDescription, user1, user2, binqty]

            logging.info(f'Seleção de nodrops efetuada com sucesso. SOMA DE NODROPS: {soma_nodrops} SOMA DE CANCELAMENTOS: {soma_cancelamentos} ')
            print(soma_nodrops, soma_cancelamentos)
            if dict_nodrops != None:
                return dict_nodrops
            else:
                return 0, 0

        except:
            logging.warning('não foi possivel efetuar o select nos nodrops')


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



    cursor, cnxx = conect_db(server, port, database, uid, pwd)

    dict_nodrops = select_nodrops(cursor, cribs, ontem, anteontem)
    #select_nodrops(cursor, cribs, ontem, anteontem)

    return dict_nodrops

