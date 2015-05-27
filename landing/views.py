from django.shortcuts import render

def home(request):
	return render(request, 'index.html')

def locals(request):
	return render(request, 'locals.html')
