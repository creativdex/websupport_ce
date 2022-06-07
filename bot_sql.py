import pyodbc
from bot_create import cfg

class sqlce:
    conn_config: str = None
    def connect_setup(driver, server, database, uid, pwd):
        """ Установка параметров подключения 
        
        Парамметры:

        Драйвер: str
        Сервер: str
        База данных: str
        Пользователь: str
        Пароль: str
        """
        driver_con: str = driver 
        server_con: str = server
        database_con: str = database
        uid_con: str = uid
        pwd_con: str = pwd

        sqlce.conn_config = f"{driver_con};{server_con};{database_con};{uid_con};{pwd_con};"
    
    def dec_connect(sql_func):
        """ 
        Декоратор для открытия и закрытия подключения к БД 
        
        Параметры: sql функция
        """
        def wrapper(*args, **kwargs):
            connconfig = f"DRIVER={cfg['SQL']['driver']};SERVER={cfg['SQL']['server']};DATABASE={cfg['SQL']['database']};UID={cfg['SQL']['uid']};PWD={cfg['SQL']['pwd']}"
            connection = pyodbc.connect(connconfig)
            cursor = connection.cursor()
            res = sql_func(cursor, *args, **kwargs)
            cursor.close()
            connection.close()
            return res
        return wrapper



def dec_connect(sql_func):
    """ Декоратор для открытия и закрытия подключения к БД """
    def wrapper(*args, **kwargs):
        connconfig = f"DRIVER={cfg['SQL']['driver']};SERVER={cfg['SQL']['server']};DATABASE={cfg['SQL']['database']};UID={cfg['SQL']['uid']};PWD={cfg['SQL']['pwd']}"
        connection = pyodbc.connect(connconfig)
        cursor = connection.cursor()
        res = sql_func(cursor, *args, **kwargs)
        cursor.close()
        connection.close()
        return res
    return wrapper


@dec_connect
def sql_check_user(cursor, user_id):
    """ Запрос в БД Проверка на наличие регистрации """
    requestString = f""" SELECT user_id, privilege FROM users WHERE  (user_id = {user_id}) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    if query == None:
        return None
    else:
        for i in query:
            for j in i:
                result.append(str(j).strip(strip))
        return result
    


@dec_connect
def sql_get_city(cursor):
    """ Запрос в БД получение городов """
    requestString = f""" SELECT DISTINCT city FROM division """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result


@dec_connect
def sql_get_division(cursor, user_id):
    """ Запрос в БД получение подразделения """
    requestString = f""" SELECT division
                    FROM     division
                    WHERE  (city = 
                            (SELECT city
                            FROM users
                            WHERE user_id = {user_id})) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result


@dec_connect
def sql_get_cashbox(cursor, division):
    """ Запрос в БД получение подразделения """
    requestString = f""" SELECT name FROM cashbox WHERE (division='{division}') """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        result.append(str(i).strip(strip))
    return result


@dec_connect
def sql_create_user(cursor, user_id, name, tel, city):
    """ Запрос в БД на создание пользователя """
    requestString = f""" INSERT INTO users (user_id, name, tel, city, privilege) VALUES 
({user_id}, '{name}', 8{tel}, '{city}', 1) """
    cursor.execute(requestString)
    cursor.commit()


@dec_connect
def sql_get_user(cursor, user_id):
    """ Запрос в БД на получение данных о пользователе """
    requestString = f""" SELECT name, tel FROM users WHERE  (user_id = {user_id}) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        for j in i:
            result.append(str(j).strip(strip))
    return result


@dec_connect
def sql_create_smart(cursor, id, message_id):
    """ Запрос в БД на создание записи об обрашении """
    requestString = f""" INSERT INTO smart (id, message_id) VALUES ({id}, {message_id}) """
    cursor.execute(requestString)
    cursor.commit()

@dec_connect
def sql_get_message(cursor, id):
    """ Запрос в БД поиск id сообщения и статуса """
    requestString = f""" SELECT message_id, complete FROM smart WHERE (id = {id}) """
    cursor.execute(requestString)
    query =  cursor.fetchall()
    strip = """ (',) """
    result = []
    for i in query:
        for j in i:
            result.append(str(j).strip(strip))
    return result

@dec_connect
def sql_complete_smart(cursor, id):
    """ Запрос в БД изменение статуса сообщения  """
    requestString = f""" UPDATE smart SET complete = 1 WHERE (id = {id}) """
    cursor.execute(requestString)
    cursor.commit()
