import mysql.connector
from mysql.connector import Error


def create_connection():
    """创建数据库连接"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='library',
            user='root',
            password='123456',
            auth_plugin='mysql_native_password'
        )
        return conn
    except Error as e:
        print(f"发生了 '{e}' 错误！")
        print("登录失败！")
        return None  # 连接失败时返回None


def close_connection(conn):
    """关闭数据库连接"""
    if conn is not None and conn.is_connected():
        conn.close()


#通过访问数据库实现登录效果
def check_login(username, password, user_type):
    # 尝试创建数据库连接
    connection = create_connection()
    if connection is None:
        print("数据库连接失败，无法继续登录验证。")
        return False
    cursor = connection.cursor()

    # 根据用户类型调整查询条件
    if user_type == 'admin':
        query = "SELECT * FROM Users WHERE username=%s AND password=%s AND role='admin'"
    else:  # 默认为普通用户
        query = "SELECT * FROM Users WHERE username=%s AND password=%s AND role='user'"

    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    close_connection(connection)

    # 根据查询结果返回登录验证状态
    if not user:
        print("查无此人，请重新选择")
    return user is not None
