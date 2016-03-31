from django.shortcuts import render
from django.http import HttpResponse

from textblob import TextBlob
import os
import urllib.parse
import urllib.request
import re
import json
#import pprint

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

    preprocess_data(data)
    return HttpResponse('Done')

def preprocess_data(data):
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
    get_result(data)
    

def get_result(data):
    results=[]
    query_string = urllib.parse.urlencode({"search_query" : data})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    print ("Number of links extracted={}".format(len(list(set(search_results)))))
    for link in search_results:
        results.append("http://www.youtube.com/wwwatch?v=" + link)
    print(results)
    return HttpResponse('Done')