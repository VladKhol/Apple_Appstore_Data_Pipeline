import pymysql

def create_connection(_host, _user, _password, _db):
    connection = pymysql.connect(host= _host,
                     user = _user,
                     password=_password,
                     db =_db,
                     charset= 'utf8mb4',
                     cursorclass= pymysql.cursors.DictCursor)

    return connection
