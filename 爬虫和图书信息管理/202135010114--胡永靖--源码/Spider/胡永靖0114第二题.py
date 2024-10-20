# 导入所需库
import requests
import json

# 定义百度翻译建议API的URL
url = 'https://fanyi.baidu.com/sug'

# 设置请求头，模拟浏览器访问以避免被服务器拒绝
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36'
}

# 要查询的关键词
word = input("请输入要查询的单词：")

# 构造POST请求的参数
data = {'kw': word}

# 发起POST请求
response = requests.post(url=url, data=data, headers=headers)

# 将响应内容解析为JSON格式
text = response.json()
print(text)  # 打印查询结果到控制台

# 根据关键词创建JSON文件名
json_filename = word + '.json'

# 将查询结果保存为JSON文件，ensure_ascii=False允许保存中文字符
with open(json_filename, 'w', encoding='utf-8') as df:
    json.dump(response.json(), df, ensure_ascii=False)

# 创建用于存储文本的TXT文件名
txt_filename = word + '.txt'

try:
    # 重新打开刚保存的JSON文件，加载其内容
    with open(json_filename, 'r', encoding='utf-8') as json_file:
        translation_data = json.load(json_file)  # 将文件内容读取为字典

        # 检查JSON数据中是否存在'data'键且其值为列表
        if 'data' in translation_data and isinstance(translation_data['data'], list):
            # 打开或创建TXT文件准备写入
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                # 遍历建议列表，每个条目写入一行
                for i, item in enumerate(translation_data['data'], start=1):  # 使用enumerate自动计数
                    txt_file.write(f"翻译[{i}]: {item['v']}\n")  # 写入翻译条目和换行符
        else:
            print("JSON文件中的数据结构不符合预期，无法找到翻译结果。")
except FileNotFoundError:
    print(f"文件{filename}未找到。")  # 如果尝试打开的文件不存在，则提示
except json.JSONDecodeError:
    print(f"{filename}文件内容不是有效的JSON格式。")  # 如果JSON文件解析出错，则提示
except Exception as e:
    print(f"处理过程中发生错误：{e}")  # 捕获并打印其他所有异常