import requests
import urllib.parse
from time import sleep

def load_page(full_url, file_name, param):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(full_url, headers=headers, params=param)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.RequestException as e:
        print(f"加载页面时发生错误：{e}")
        return None

def write_page(html, file_name):
    try:
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(html)
        print(f"正在保存{file_name}")
    except Exception as e:
        print(f"保存错误，发生了Error：{e}")

def sogou_spider(url, fileName, begin_page, end_page, param):
    for page in range(begin_page, end_page + 1):
        full_url = f"{url}{param['query']}&page={page}"
        page_file_name= f"{fileName}_{page}页.html"
        print(f"正在读取{page_file_name}")
        html = load_page(full_url,page_file_name, param)
        if html:
            write_page(html, page_file_name)
            sleep(1.5)  # 避免频繁请求，模拟延迟
    print("所有页面爬取完毕。")



def get_user_input(prompt, type_func=int, error_msg="输入无效，请重新输入"):
    """获取用户输入并进行类型转换，提供错误处理"""
    while True:
        user_input = input(prompt)
        try:
            return type_func(user_input)
        except ValueError:
            print(error_msg)

def main():
    print("欢迎使用搜狗网页爬虫工具！")

    # 输入关键词并进行URL编码
    kw = input("请输入搜索关键词：")
    encoded_kw = urllib.parse.quote(kw)  # 对关键词进行URL编码
    param = {'query': encoded_kw}

    # 输入起始页和终止页，带有错误处理
    begin_page = get_user_input("请输入起始页：", error_msg="起始页必须是整数。")
    end_page = get_user_input("请输入终止页：", error_msg="终止页必须是整数。")

    # 定义搜狗搜索的URL前半部分
    front_url = "https://www.sogou.com/web?query="

    # 调用sogou_spider方法
    try:
        sogou_spider(front_url, kw, begin_page, end_page, param)
    except Exception as e:
        print(f"爬取过程中发生错误：{e}")


if __name__ == "__main__":
    main()