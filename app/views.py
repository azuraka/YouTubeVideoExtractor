from django.shortcuts import render
from django.http import HttpResponse 
from textblob import TextBlob
from collections import OrderedDict
from bs4 import BeautifulSoup
import os, re, json, urllib.parse, urllib.request


# to render home page
def index(request):
    results2={}
    return render(request, 'app/index.html', results2)


# uploads the news article and stores it at local system
def file_upload(request):
    if request.method == 'POST':
        filename = str(request.FILES['file'])
        if not os.path.exists(os.getcwd() + '/static/articles'):
            os.mkdir(os.getcwd() + '/static/articles')
        with open(os.getcwd() + '/static/articles/{}'.format(request.FILES['file']), 'wb+') as destination:
            for chunk in request.FILES['file']:
                destination.write(chunk)
        with open(os.getcwd() + '/static/articles/{}'.format(request.FILES['file']), 'r') as article:
            data_hindi = json.load(article)

        results = preprocess_data(data_hindi)
        return HttpResponse(results)


# All preprocessing of data goes here
def preprocess_data(data_hindi):
    title_hindi = data_hindi["title"]
    title_english = str(TextBlob(title_hindi).translate(to="en"))

    text_hindi = data_hindi["text"]
    text_english = str(TextBlob(text_hindi).translate(to="en"))

    #keywords_list = data_hindi["keywords"].split(',')
    #for index, term in enumerate(keywords_list):
    #    term = term.strip()
    #    blob = TextBlob(term)
    #    try:
    #        keywords_list[index] = str(blob.translate(to="en"))
    #    except:
    #        pass
    #keywords_english = ' '.join(keywords_list)
    #print (title_hindi)
    #print (title_english)
    #print (text_hindi)
    #print (text_english)
    
    #sentiment_analysis(text_english)
    #noun_phrases(text_english)
    #parts_of_speech(text_english)

    query_hindi = create_search_query(title_hindi, text_hindi)
    query_english = create_search_query(title_english, text_english)
    #print (query_hindi)
    #print (query_english)
    results = search_youtube(query_hindi, query_english)
    return results


# Sentiment Analysis of news article text
def sentiment_analysis(text_english):
    blob = TextBlob(text_english)
    print (blob.sentiment)
    #return str(blob.sentiment)


# Noun Phrase Identification over the text 
def noun_phrases(text_english):
    blob = TextBlob(text_english)
    print (blob.noun_phrases)
    #return str(blob.noun_phrases)


# Parts of speech for each word
def parts_of_speech(text_english):
    blob = TextBlob(text_english)
    print (blob.tags)
    #return blob.tags


# Create Search Query by removing the terms from title based upon inverted index of text
def create_search_query(title, text):
    inverted_index = {}
    title = list(TextBlob(title).words)
    text = list(TextBlob(text).words)
    for word in text:
        if word in inverted_index.keys():
            inverted_index[word]+=1
        else:
            inverted_index[word]=1
    #print (inverted_index)
    for word in title:
        if word in inverted_index.keys():
            if inverted_index[word]<2:
                title.remove(word)
        else:
            title.remove(word)
    query = " ".join(title)
    #print (query)
    return query


# Generating all possible n-gram combinations
def n_grams(query):
    query_list=[]
    words_query = TextBlob(query).words
    blob = TextBlob(query)
    query_length=len(words_query)
    for n in range(query_length, 2, -1):
        combination_list = blob.ngrams(n=n)
        for par in combination_list:
            query_list.append(" ".join(par))
    return query_list


# Actual query search going here
def search_youtube(query_hindi, query_english):
    query_list_inorder_hindi = n_grams(query_hindi)
    query_list_inorder_english = n_grams(query_english)
    #print (query_list_inorder_hindi)
    #print (query_list_inorder_english)
    
    results=OrderedDict()
    count = 0
    
    for query in query_list_inorder_hindi:
        if(count<5):
            query_string = urllib.parse.urlencode({"search_query" : query})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            soup = BeautifulSoup(html_content.read().decode(), 'html.parser')
            titles = []
            links = []
            for link in soup.find_all('a'):
                if(count<5):
                    if link.get('href')[0:6] == '/watch' and '&list=' not in link.get('href'):
                        if link.get('title') != None:
                            #titles.append(link.get('title'))
                            #links.append('http://www.youtube.com' + link.get('href'))
                            if link.get('title') not in results.keys():
                                results[link.get('title')] = 'http://www.youtube.com' + link.get('href')
                                count+=1
                else:
                    break
        else:
            break

    count=0
    for query in query_list_inorder_english:
        if(count<5):
            query_string = urllib.parse.urlencode({"search_query" : query})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            soup = BeautifulSoup(html_content.read().decode(), 'html.parser')
            titles = []
            links = []
            for link in soup.find_all('a'):
                if(count<5):
                    if link.get('href')[0:6] == '/watch' and '&list=' not in link.get('href'):
                        if link.get('title') != None:
                            #titles.append(link.get('title'))
                            #links.append('http://www.youtube.com' + link.get('href'))
                            if link.get('title') not in results.keys():
                                results[link.get('title')] = 'http://www.youtube.com' + link.get('href')
                                count+=1
                else:
                    break
        else:
            break

    print(results)
    converted_string=""
    for key, value in results.items():
        converted_string+=key+"***"+value+"|||"
    return converted_string
