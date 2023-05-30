from pyecharts.charts import WordCloud
import requests
from bs4 import BeautifulSoup
import re
import collections
import sys
import jieba
import os
import json


inp = sys.argv[1]
dir = '/var/www/html/wordcloud/'
VIDEOINFOURL = 'https://api.bilibili.com/x/space/arc/search?mid='

def getFiletxt(path):
    return open(path, 'r', encoding='utf-8').read().split('\n')[0:-1]
def init():
    if not os.path.exists(dir + inp + '.html'):
        open(dir + inp + '.html', 'w+').write('请耐心等待')

    else:
        print("文件已存在")
        sys.exit()
    print("文件读取中")
    
    # with open('/home/stop_words.txt', "r", encoding='utf-8') as f:
    #     print("文件读取完毕")
    #     con = f.readlines()
    #     stop_words = set()
    #     for i in con:
    #         i = i.replace("\n", "")
    #         stop_words.add(i)


def get_cid(bvid):
    cid_list = []
    r = json.loads(requests.get('https://api.bilibili.com/x/player/pagelist?bvid=' + bvid).text)
    for data in r['data']:
        cid_list.append(data['cid'])
    return cid_list


def get_cid_list(bvid, mid):
    cid_list = []
    if not mid:
        return get_cid(bvid)
    for i in range(1, 5):
        r = json.loads(requests.get(
            'https://api.bilibili.com/x/space/arc/search?mid=' + str(mid) + '&pn=+' + str(i) + '&ps=50').text)
        for j in r['data']['list']['vlist']:
            cid_list.extend(get_cid(j['bvid']))
    return cid_list


def get_barrage(cid_list, result_list):
    stop_words = getFiletxt('/home/stop_words.txt')
    for cid in cid_list:
        req = requests.get('https://comment.bilibili.com/' + str(cid) + '.xml')
        req.encoding = req.apparent_encoding
        soup = BeautifulSoup(req.text, 'html.parser').find_all(name='d')
        result = ""
        for i in soup:
            s = re.sub('<(.*?)>', '', str(i))
            result += s + "\n"
        seg_list_exact = jieba.cut(result, cut_all=True)
        for word in seg_list_exact:
            if word not in stop_words and len(word) > 1:
                result_list.append(word)


def get_wordCloud(result_list, dir):
    print("1")
    word_counts = collections.Counter(result_list)
    print("2")
    word_counts_top100 = word_counts.most_common(100)
    print("3")
    # print(word_counts_top100)

    mywordcloud = WordCloud()
    print("4")
    mywordcloud.add('', word_counts_top100, shape='circle')
    print("5")

    ### 指定渲染图片存放的路径
    mywordcloud.render(dir)


if __name__ == '__main__':


    bvid = 0
    mid = 0

    if "BV" in inp and len(inp) < 13 and inp.isalnum():
        bvid = inp
    elif str.isdigit(inp):
        mid = inp
    else:
        print("输入有误")
        sys.exit()
    init()
    print("初始化完成")
    cid_list = get_cid_list(bvid, mid)
    print("cid获取成功")
    result_list = []
    get_barrage(cid_list, result_list)
    print("弹幕获取成功")
    get_wordCloud(result_list, dir + inp + '.html')
    print("ok")


