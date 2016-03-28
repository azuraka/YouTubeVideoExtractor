from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	context = {}
	return render(request, 'app/index.html', context)

def file_upload(request):
	print request.FILES['file']
	return HttpResponse('Done')