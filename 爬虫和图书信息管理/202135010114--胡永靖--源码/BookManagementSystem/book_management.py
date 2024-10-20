import mysql.connector
from mysql.connector import Error
from Book import Book

class BookManager:
    def __init__(self, host, user, password, database,user_type,loginname):
        self.connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
        self.user_type = user_type
        self.loginname = loginname
        self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("MySQL connection is closed")

    #用户模块
    # 从数据库中拿出所有图书信息，并实例化
    def fetch_books(self):
        try:
            query = "SELECT * FROM Books"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            books = [Book(row[0], row[1], row[2], row[3], row[4]) for row in rows]
            return books
        except Error as e:
            print(f"Error fetching books: {e}")
            return []

    # 通过遍历Book的对象列表，打印出每本书的信息
    def display_books(self):
        books = self.fetch_books()
        for book in books:
            #打印Book对象
            print(book)

    #搜索书籍
    def search_books(self, keyword, field='title'):
        try:
            query = f"SELECT * FROM Books WHERE {field} LIKE %s"
            self.cursor.execute(query, ('%' + keyword + '%',))
            rows = self.cursor.fetchall()
            for row in rows:
                yield Book(*row)  # 使用生成器返回结果，节省内存
        except Error as e:
            print(f"找不到此书: {e}")
    #还书
    def return_book(self, book_title,borrow_id):
        try:
           # 确认借阅记录
            check_query = "SELECT id FROM BorrowRecords WHERE book_id = (SELECT id FROM Books WHERE title = %s) AND id = %s AND return_date IS NULL"
            self.cursor.execute(check_query, (book_title, borrow_id))
            borrow_record_id = self.cursor.fetchone()
            if not borrow_record_id:
                print(f"当前用户没有此书（ '{book_title}'）的借阅记录 )")
                return
            # 更新图书数量
            update_book_query = "UPDATE Books SET quantity = quantity + 1 WHERE title = %s"
            self.cursor.execute(update_book_query, (book_title,))

            # 更新借阅记录的归还日期
            update_borrow_query = "UPDATE BorrowRecords SET return_date = CURRENT_DATE WHERE id = %s"
            self.cursor.execute(update_borrow_query, (borrow_record_id[0],))

            self.connection.commit()
            print(f"书名： '{book_title}'成功归还 ")
        except Error as e:
            print(f"还书发生错误: {e}")
    #借书
    def borrow_book(self, book_title, borrower_username):
        try:
            # 查询用户ID
            self.cursor.execute("SELECT id FROM Users WHERE username = %s", (borrower_username,))
            user_info = self.cursor.fetchone()
            if not user_info:
                print(f"该 '{borrower_username}'用户不存在！")
                return
            user_id = user_info[0]
            # 查询图书信息
            self.cursor.execute("SELECT id, quantity FROM Books WHERE title = %s", (book_title,))
            book_info = self.cursor.fetchone()
            if not book_info:
                print(f"未找到该书： '{book_title}'.")
                return
            book_id, quantity = book_info
            if quantity <= 0:
                print(f"该书 （'{book_title}'）当前不可借阅。 ")
                return
            # 更新图书数量
            update_query = "UPDATE Books SET quantity = quantity - 1 WHERE id = %s"
            self.cursor.execute(update_query, (book_id,))
            # 插入借阅记录
            insert_borrow_query = "INSERT INTO BorrowRecords (book_id, user_id, borrow_date, due_date) VALUES (%s, %s, CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 14 DAY))"
            self.cursor.execute(insert_borrow_query, (book_id, user_id))
            self.connection.commit()
            print(f"该书（ '{book_title}'） 成功借阅给 （'{borrower_username}'）用户.")
        except Error as e:
            print(f"发生借阅错误: {e}")

    # 查看特定用户名用户的借阅
    def view_borrowed_books_by_username(self, borrower_username):
        try:
            # 假设BorrowRecords表有book_id, user_id, borrow_date, due_date字段
            query = """
                SELECT b.id, b.title, b.author, b.publication_year, ub.due_date 
                FROM Books b 
                INNER JOIN BorrowRecords ub ON b.id = ub.book_id 
                INNER JOIN Users u ON ub.user_id = u.id 
                WHERE u.username = %s AND ub.return_date IS NULL
            """
            self.cursor.execute(query, (borrower_username,))
            rows = self.cursor.fetchall()
            borrowed_records = []
            for row in rows:
                # 调整book_info字典以匹配实际查询结果
                book_info = {
                    'book_id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'publication_year': row[3],
                    'due_date': row[4],  # 增加预计归还日期
                }
                borrowed_records.append(book_info)
            return borrowed_records
        except Error as e:
            print(f"发生错误: {e}")
            return []

    # 添加图书
    def add_book_admin(self, title, author, publication_year, quantity=1):

        try:
            # 准备SQL插入语句
            query = """
                INSERT INTO Books (title, author, publication_year,  quantity)
                VALUES (%s, %s, %s, %s)
            """

            values = (title, author, publication_year, quantity)

            # 执行SQL语句
            self.cursor.execute(query, values)

            # 提交事务
            self.connection.commit()

            print(f"书本'{title}'添加成功！ ")
        except Error as e:
            # 如果发生错误，回滚事务并打印错误信息
            self.connection.rollback()
            print(f"Error adding book: {e}")

    #获取当前所选的图书ID
    def get_book_id_by_title(self, title):
        """根据书名获取图书ID"""
        query = "SELECT id FROM Books WHERE title = %s"
        self.cursor.execute(query, (title,))
        book_id = self.cursor.fetchone()
        return book_id[0] if book_id else None

    #管理有修改权限
    def update_book_by_name(self, book_title):
        # 根据书名查找图书ID
        book_id = self.get_book_id_by_title(book_title)
        if not book_id:
            print("此书未找到！")
            return
        # 获取用户想要更新的字段信息
        print("输入图书的新信息(留空以保留当前值。)")
        new_title = input("新的图书名称: ") or None
        new_author = input("新的作者: ") or None
        new_year = input("新的出版年份: ")
        if new_year:
            new_year = int(new_year)  # Convert to int if provided
        else:
            new_year = None
        new_quantity = input("要修改的数量！ ")
        if new_quantity:
            new_quantity = int(new_quantity)  # Convert to int if provided
        else:
            new_quantity = None
        # 执行更新
        self.update_book(book_id, new_title, new_author, new_year, new_quantity)

    def update_book(self, book_id, new_title=None, new_author=None, new_year=None,
                            new_quantity=None):
        # 获取当前图书信息
        current_book = self.find_book_by_id(book_id)
        if not current_book:
            print("要修改的图书未找到。")
            return
        # 更新字段（仅当提供了新值时）
        if new_title: current_book.title = new_title
        if new_author: current_book.author = new_author
        if new_year: current_book.publication_year = new_year
        if new_quantity: current_book.quantity = new_quantity
        try:
            query = "UPDATE Books SET title=%s, author=%s, publication_year=%s, quantity=%s WHERE id=%s"
            values = (
            current_book.title, current_book.author, current_book.publication_year, current_book.quantity,book_id)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f" {current_book.title} 成功更新。")
        except Error as e:
            print(f"发生更新错误: {e}")

        # 查找图书通过ID

    def find_book_by_id(self, book_id):
        try:
            query = "SELECT * FROM Books WHERE id=%s"
            self.cursor.execute(query, (book_id,))
            row = self.cursor.fetchone()
            return Book(*row) if row else None
        except Error as e:
            print(f"找不到此书！")
            return None

    def delete_book_example(self, del_title):
        # 检查是否有未归还的借阅记录
        book_id = self.get_book_id_by_title(del_title)
        has_outstanding_borrows = self.check_outstanding_borrows(book_id)
        if has_outstanding_borrows:
            print("你还不能删除此书！！！！")
            return

        confirm = input(f"你确定要删除此书（ {del_title}）吗? (yes/no): ")
        if confirm.lower() == 'yes':
            self.delete_book(book_id,del_title)
        else:
            print("取消删除.")

    def check_outstanding_borrows(self, book_id):
        """检查是否有未归还的借阅记录"""
        query = "SELECT COUNT(*) FROM BorrowRecords WHERE book_id = %s AND return_date IS NULL"
        self.cursor.execute(query, (book_id,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def delete_book(self, book_id,del_title):
        try:
            query = "DELETE FROM Books WHERE id=%s"
            self.cursor.execute(query, (book_id,))
            self.connection.commit()
            print(f"{del_title} 被成功删除")
        except Error as e:
            print(f"发生删除错误: {e}")

    def print_meau(self):
        while True:
            print("\n"+"=" * 32 + "图书管理系统" + "=" * 32)
            print("1. 查看书目")
            print("2. 归还图书")
            print("3. 搜索图书")
            print("4. 借阅图书")
            print("5. 查看借阅")
            print("6. 添加图书")
            print("7. 修改图书")
            print("8. 删除图书")
            print("0. 退出系统")
            print("（备注：0-5为公共权限，6-8则需要管理权限！）")
            choice = input("请选择操作：")
            if choice == '1':
                self.fetch_books()
                self.display_books()
            elif choice == '2':
                book_title = input("请输入要归还的书名：")
                # 首先，通过用户名找到对应的用户ID
                try:
                    borrowid = int(input("请输入还书ID"))
                except:
                    print("输入有误！")
                self.return_book(book_title,borrowid)
            elif choice == '3':
                keyword = input("请输入搜索关键词：")
                field = input("按哪个字段搜索？(标题、作者；默认：标题)（）：") or 'title'
                if field == '标题' or field == 'Title' or field == 'title':
                    field = 'title'
                elif field == '作者':
                    field = 'author'
                results = list(self.search_books(keyword, field))
                print("\n搜索结果：")
                for book in results:
                    print(book)
            elif choice == '4':
                title = input("请输入要借阅的图书名称（title）：")
                self.borrow_book(title,self.loginname)
            elif choice == '5':
                borrowed_books = self.view_borrowed_books_by_username(self.loginname)
                if borrowed_books:
                    for book in borrowed_books:
                        print(book)
                else:
                    print("无借阅记录！")
            elif choice == '0':
                print("感谢使用图书管理系统，再见！")
                break
            elif self.user_type =='admin' and choice == '6':
                    new_title = input("请输入图书的名称：")
                    new_author = input("请输入图书作者：")
                    new_publication_year = input("请输入发行日期：")
                    while True:
                        try:
                            new_quantity = int(input("请输入你要添加的数量："))
                            if new_quantity >= 1:
                                break
                        except:
                            print("输入有误，请重新输入数量")
                    self.add_book_admin(new_title,new_author,new_publication_year,new_quantity)
            elif self.user_type =='admin' and choice == '7':
                book_title = input("请输入要修改的图书名称：")
                self.update_book_by_name(book_title)
            elif self.user_type =='admin' and choice == '8':
                del_title = input("请输入要删除的图书名称：")
                self.delete_book_example(del_title)
            else:
                print("无效的选择，请重新输入。")

