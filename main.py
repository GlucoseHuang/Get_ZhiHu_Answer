from ZhiHu import getAnswer

# 获取questions.txt中的全部问题，并获取回答，保存到output文件夹

fp = open("questions.txt", "r")
for i in fp.read().split():
    getAnswer(i)
fp.close()
