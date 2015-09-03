from django.shortcuts import render
from django.template.context_processors import csrf


def main(request):
	context = {}
	context.update(csrf(request))
	return render(request, 'chat-main.html', context)


