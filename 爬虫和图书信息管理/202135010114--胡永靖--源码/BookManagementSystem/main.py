# from BookManagementSystem.Login import check_login
# from BookManagementSystem.book_management import BookManager
import Login
import book_management
def main():
    print("=" * 30 + "欢迎来到图书管理系统" + "=" * 30)
    print("=" * 30 + "      请登录        " + "=" * 30)
    panduan = True
    while panduan:
        type = int(input("请问需要以管理员身份登录还是用户身份登录：（按1：管理员）、（按2：用户）"))
        if type == 1:
            user_type = 'admin'
        elif type == 2:
            user_type = 'user'
        else:
            print("输入有误，请重新输入！")
            continue
        username = input("请输入用户名: ")
        password = input("请输入密码: ")
        if Login(username, password,user_type):
            panduan = False
            print("登录成功！")
            book_manager = book_management('localhost', 'root', '123456', 'library',user_type,username)
            book_manager.print_meau()

        else:
            print("用户名或密码错误！请重新输入！")



if __name__ == "__main__":
    main()