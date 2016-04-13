from django.shortcuts import render
from django.http import HttpResponse
import pickle
import math
import json
import codecs
import math
import operator

from textblob import TextBlob
import itertools
import os
import urllib.parse
import urllib.request
import re
import json
#import pprint
import lxml
from lxml import etree
import urllib

def index(request):
    context = {}
    return render(request, 'app/index.html', context)

def file_upload(request):
    filename = str(request.FILES['file'])
    if not os.path.exists(os.getcwd() + '/static/articles'):
                os.mkdir(os.getcwd() + '/static/articles')
    with open(os.getcwd() + '/static/articles/{}'.format(request.FILES['file']), 'wb+') as destination:
                for chunk in request.FILES['file']:
                    destination.write(chunk)
    with open(os.getcwd() + '/static/articles/{}'.format(request.FILES['file']), 'r') as article:
        data = json.load(article)

    preprocess_data(data,filename)
    return HttpResponse('Done')

s = {}

def preprocess_data(data,filename):
    keywords_list = data["keywords"].split(',')
    for index, term in enumerate(keywords_list):
        term = term.strip()
        blob = TextBlob(term)
        try:
            keywords_list[index] = str(blob.translate(to="en"))
        except:
            pass
    data = ' '.join(keywords_list)
    for sentence in blob.sentences:
        print("Polarity={}".format(sentence.sentiment.polarity))
    get_result(data,filename)
    
def extractTitle(path):
    l = ['donald trump h1b visa', 'controversy on donald trump on h1b visa','donald trump', 'donald trump', 'donald duck','donald trump contesting for us presidency']
    word_dictionary = {}
    data = []
    with codecs.open('/home/manohar/Desktop/PyDev Eclipse/Workspace/IRE_Major/YouTubeVideoExtractor/static/articles/'+path,'rU','utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    title = data[0]['title']
    t = u'|'
    l = data[0]['text'].split(u'\u0964')
    
    for i in range(len(l)):
        p = l[i].split(' ')
        for j in range(len(p)):
            if p[j] in word_dictionary:
                if i in word_dictionary[p[j]]:
                    word_dictionary[p[j]][i] = word_dictionary[p[j]][i] + 1
                else:
                    word_dictionary[p[j]][i] = 1
            else:
                word_dictionary[p[j]] = {}
                word_dictionary[p[j]][i] = 1
    word_dic = {}
    N = len(l)
    for key in word_dictionary:
        df = len(word_dictionary[key].keys())
        word_dic[key] = df
    wordlis = []
    for key in word_dic:
        if word_dic[key] >= 2:
            wordlis.append(key)
    p = title.split(' ')
    new_list = []
    for i in range(len(p)):
        if p[i] in wordlis:
            new_list.append(p[i])
    s = ''
    for i in range(len(new_list)):
        s = s + ' ' + new_list[i]
    return s


def RankResults(l,s):
    #l = ['donald trump h1b visa', 'controversy on donald trump on h1b visa','donald trump', 'donald trump', 'donald duck','donald trump contesting for us presidency']
    word_dictionary = {}
    
    for i in range(len(l)):
        p = l[i].split(' ')
        for j in range(len(p)):
            if p[j] in word_dictionary:
                if i in word_dictionary[p[j]]:
                    word_dictionary[p[j]][i] = word_dictionary[p[j]][i] + 1
                else:
                    word_dictionary[p[j]][i] = 1
            else:
                word_dictionary[p[j]] = {}
                word_dictionary[p[j]][i] = 1
    word_dic = {}
    N = len(l)
    for key in word_dictionary:
        df = len(word_dictionary[key].keys())
        word_dic[key] = math.log(N/float(df))
    #s = 'donald trump h1b visa cancellation controversy'
    #s = 'donald contesting for us presidency'
    k = s.split(' ')
    score = 0
    list_scores = [0 for i in range(len(l))]
    for i in range(len(k)):
        for j in range(len(l)):
            if k[i] in l[j]:
                list_scores[j] = list_scores[j] + word_dic[k[i]]
    for i in range(len(l)):
        for j in range(len(l)):
            if list_scores[i] > list_scores[j]:
                temp = list_scores[i]
                list_scores[i] = list_scores[j]
                list_scores[j] = temp
                temp = l[i]
                l[i] = l[j]
                l[j] = temp

def get_result(data,filename):
    results=[]
    data_new = extractTitle(filename)
    query_string = urllib.parse.urlencode({"search_query" : data})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    print(data_new)
    print ("Number of links extracted={}".format(len(list(set(search_results)))))
    for link in search_results:
        results.append("http://www.youtube.com/watch?v=" + link)
    for i in range(len(results)):
        youtube = etree.HTML(urllib.request.urlopen(results[i]).read())
        video_title = youtube.xpath("//span[@id='eow-title']/@title")
        s[''.join(video_title)] = 1
    #print(results)
    RankResults(s,data_new)
    for i in range(len(s)):
        print(s)
    return HttpResponse('Done')