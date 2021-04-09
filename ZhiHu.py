import requests
import re
import json
from time import sleep
from html2text import HTML2Text

# 获取答案
def getAnswer(questionId):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.72",
    }
    sleepTime = 1
    limit = 5

    # 开始读取题目页面
    url = f"https://www.zhihu.com/question/{questionId}"
    response = requests.get(url, headers=headers)
    answerCount = int(re.findall(r'"answerCount":(.*?),', response.text)[0])
    questionTitle = re.findall('<title.*?>(.*?) - 知乎</title>', response.text)[0].replace("?", "？")

    # 新建文件，写入标题
    print(f"问题：{questionTitle} ID:{questionId}")
    fp = open(rf".\output\{questionTitle} {questionId}.md", "a+", encoding="utf-8")
    fp.write(f"# [{questionTitle}]({url})\n\n")

    # 开始一一获取回答
    for i in range(0, (answerCount // 5) + 1):

        sleep(sleepTime)

        # 回答按默认顺序排列，每次读取limit个回答
        offset = i * limit
        url = f"https://www.zhihu.com/api/v4/questions/{questionId}/answers?include=data.comment_count,content,voteup_count;author.name" \
              f"&limit={limit}&offset={offset}&platform=desktop&sort_by=default"

        response = requests.get(url, headers=headers)
        datas = json.loads(response.text)["data"]

        # 一一获取回答中的内容，写入文件

        for j, data in enumerate(datas):

            print(f"\t读取回答...{offset + j + 1}/{answerCount}")

            # 如果作者没有匿名，则读取简介
            description = ""
            if data['author']['url_token'] != '':
                sleep(sleepTime)
                url = f"https://www.zhihu.com/people/{data['author']['url_token']}"
                response = requests.get(url, headers=headers)
                descriptionPtn = re.compile(
                    '<meta data-react-helmet="true" name="description" property="og:description" content="(.*?) 回答数.*?"/>'
                )
                try:
                    description = descriptionPtn.findall(response.text)[0].strip()
                except IndexError:
                    description = ''
            else:
                url = ''

            # 如果简介为空，就不用加冒号
            if description != '':
                description = ": " + description

            # 写入名字和简介
            fp.write(f"#### ({offset + j + 1}) [[{data['author']['name']}{description}]{'(' + url + ')'}] ")

            # 写入赞同数
            fp.write(f"[赞同: {data['voteup_count']}]\n")

            # 写入图文内容
            content = data["content"]
            rawText = HTML2Text().handle(content)
            trashPtn = re.compile("!\[]\(data:image.*?\)", re.DOTALL)
            text = re.sub(trashPtn, "", rawText)
            fp.write(text)

            # 写入原回答地址
            url = f"https://www.zhihu.com/question/{questionId}/answer/{data['id']}"
            fp.write(f"[原文链接]({url})")

            # 写完一个回答后空行
            fp.write("\n\n")

    fp.close()
