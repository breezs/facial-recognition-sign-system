import pymysql
def connectMySQL():
    # 连接数据库
    database = pymysql.Connect(  # 连接数据库
        host='localhost',
        port=3306,
        user='root',
        passwd='zs20010926',
        db='test',
        charset='utf8',
    )
    return database