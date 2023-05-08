import pyodbc
import cryptocode
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
    except Exception as e:
        print(e)
        logging.error(f'não foi possivel conectar ao banco de dados - {e}')


def select_trans_nodrop(eventdate, anteontem, employee, cribin,
                        cursor, index):  # seleciona todas as transações especificadas no nodrop
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
        logging.info('transações de nodrop selecionadas com sucesso.')
        if len(list_trans_nodrop) >= index:
            return list_trans_nodrop[:index] #ADICIONADO O INDEX, AGORA SE POSSUI 2 NODROPS A SER FEITO ELE VAI ADICIONAR
                    #NA LISTA E RETORNAR DE ACORDO COM A QUANTIDADE DE NODROP
        else:
            return list_trans_nodrop[0]


    except Exception as e:
        print(e)
        logging.warning(f'Não foi possivel selecionar as transações de nodrop - {e}')


def select_nodrops(cursor, cribs, ontem, anteontem):
        def remove_repetidos(lista):
            l = []
            for i in lista:
                if i not in l:
                    l.append(i)
            l.sort()
            return l


        def count_cancel(cursor, employee, cribin, anteontem, ontem):
            # print(employee, cribin)
            cursor.execute(
                f"select transnumber, RelatedKey, crib, bin, item, employee, Transdate, quantity, TypeDescription, User1, User2, binqty "
                f"from Trans where issuedto = '{employee}' and TypeDescription = 'ISSUE' and status = 1 and CribBin = '{cribin}' and (transdate = CONVERT(datetime, '{anteontem}T00:00:00') or transdate >= CONVERT(datetime, '{ontem}T00:00:00'))")
            transacoes = cursor.fetchall()
            # print(len(transacoes), 'cancelamentos')
            # print(transacoes)
            # print('transações', len(transacoes))
            return len(transacoes)

        try:
            logging.info('Iniciando pesquisa de nodrops')
            cursor.execute(
                    f"select EventLogDate, EventLogMessage from EventLog where EventLogKey is null and EventLogProgramName = 'CribMaster' and EventLogDate BETWEEN CONVERT(datetime, '{anteontem}T23:00:00') AND CONVERT(datetime, '{ontem}T23:59:59');")
            nodrops = cursor.fetchall() # pega todos os nodrops do banco

            list_eventlog = []
            dict_nodrops = {}
            soma_nodrops = 0  # soma o numero de nodrops
            soma_cancelamentos = 0  # soma o numero de transações que foram canceladas manualmente
            soma_trans = 0  # soma o numero de transações que foram canceladas pelo sistema
            soma_trans_true = 0  # soma o numero de transações que podem ser canceladas
            soma_unfind = 0  # soma a quantidade de transações que não foram encontradas


            for i in nodrops:
                '''Limpa a msg sobre o crib extraindo os dados'''
                msg = i[1].split(' ')
                if msg[0] == 'No' and msg[1] == 'Drop' and msg[2] == 'detected':  #filtra pelo incio da frase
                    employee = msg[8]
                    cribin = msg[-1]
                    crib = cribin.split('-')
                    crib = int(crib[0])
                    eventlogdate = i[0].strftime('%Y-%m-%d')

                    if crib in cribs: #seleciona apenas os cribs selecionados no main e adiciona a lista de nodrops
                        list_eventlog.append([employee, cribin, crib, eventlogdate])

            list_eventlog_base = remove_repetidos(list_eventlog)  # remove nodrops repetidos para realizar a contagem a baixo
            # print(list_eventlog_base)
            '''---------------------------------'''
            for nodrop_unic in list_eventlog_base: #Para cada nodrop unico no eventlog separa os dados para realizar a contagem na função conunt_cancel
                employee = nodrop_unic[0]
                cribin = nodrop_unic[1]
                # crib = nodrop_unic[2]
                # eventlogdate = nodrop_unic[3]
                contagem = list_eventlog.count(nodrop_unic)  # conta quantidade de nodrops
                # print(contagem, 'nodrop')

                count_cancel_var = count_cancel(cursor, employee, cribin, anteontem, ontem)  # conta quantidade de cancelamentos para cada nodrop unico
                # print(count_cancel_var, 'cancelamentos')
                soma_cancelamentos += count_cancel_var #statisticas
                soma_nodrops += contagem #statisticas


                cancl_to_do = contagem - count_cancel_var #nodrops que podem ser realizados
                # print(contagem, count_cancel_var)

                while cancl_to_do != 0:


                    soma_trans_true += 1  # statisticas soma o numero de transações que podem ser canceladas


                    trans_total = select_trans_nodrop(ontem, anteontem, employee, cribin, cursor, cancl_to_do)  # chama a função que retornara a transação.
                    # print('transtotal', trans_total)
                    # caso a transação ja tenha sido cancelada manualmente ela vai retornar none
                    cancl_to_do -= 1  # diminui a quantidade de nodrops que não foram realizados
                    if trans_total is not None:
                        soma_trans += 1  # soma o numero de transações que foram canceladas pelo sistema
                        for trans in trans_total:
                            '''adiciona a transação no dicionario'''
                            trans = trans.split(',')
                            transnumber = trans[0].replace("'", '')
                            crib = trans[1].replace(' ', '')
                            bin = trans[2].replace(' ', '')
                            item = trans[3].replace(' ', '')
                            employee = trans[4].replace(' ', '')
                            Transdate = trans[5]
                            quantity = trans[6].replace(' ', '')
                            TypeDescription = trans[7].replace(' ', '')

                            user1 = trans[8].replace(' ', '')
                            if user1 == None:
                                user1 = ''
                            user2 = trans[9].replace(' ', '')
                            if user2 == None:
                                user2 = ''
                            binqty = trans[10].replace(' ', '')

                            dict_nodrops[transnumber] = [str(crib), bin, item, employee, str(Transdate), str(quantity),
                                                         TypeDescription, user1, user2, binqty]
                    else:
                        # print(trans)
                        soma_unfind += 1  # soma a quantidade de transações que não foram encontradas

            logging.info(f'Nodrops encontrados: {soma_nodrops}, Cancl encontrados: {soma_cancelamentos},Nodrops possiveis: {soma_trans_true}, total de cancelamentos efetuados: {soma_trans}, quantidade de transações que não foram encontradas : {soma_unfind}')
            print(f'Nodrops encontrados: {soma_nodrops}, Cancl encontrados: {soma_cancelamentos},Nodrops possiveis: {soma_trans_true}, total de cancelamentos efetuados: {soma_trans}, quantidade de transações que não foram encontradas : {soma_unfind}')


            if dict_nodrops != None:
                return dict_nodrops
            else:
                return 0, 0

        except Exception as e:
            # print(e)
            logging.warning(f'não foi possivel efetuar o select nos nodrops - {e}')


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

