from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.template.context_processors import csrf
from django.db.models import Q
from django.contrib.auth.models import User
import chat.models
import json


def main(request):
	context = {}
	if request.user.is_authenticated():
		context['info'] = {'name': request.user.username}
		return render(request, 'chat.html', context)
	return redirect('/admin/login/?next=/chat/')


def get_friend_list(request):
	response = {}
	if not request.user.is_authenticated():
		response['success'] = False
		response['message'] = 'Not authenticated'
		return HttpResponse(json.dumps(response))

	friend_list = []
	connects = chat.models.Connect.objects.filter(Q(user1=request.user) | Q(user2=request.user))
	for connect in connects:
		friend = connect.get_friend(request.user)
		sentences = _get_sentences(request.user, friend)
		if sentences.count():
			latest_words = sentences[0].words
		else:
			latest_words = ''
		friend_list.append({
			'name': friend.username,
			'latest_words': latest_words,
			'user_id': friend.id,
		})

	response['success'] = True
	response['data'] = friend_list

	return HttpResponse(json.dumps(response))


def get_conversation(request):
	response = {}
	if not request.user.is_authenticated():
		response['success'] = False
		response['message'] = 'Not authenticated'
		return HttpResponse(json.dumps(response))

	friend_id = request.GET.get('friend_id', None)
	if not friend_id:
		response['success'] = False
		response['message'] = 'Bad parameters'
		return HttpResponse(json.dumps(response))

	friend = User.objects.get(id=friend_id)

	conversation = []
	sentences = _get_sentences(request.user, friend)
	for sentence in sentences:
		conversation.append({
			'name': sentence.sender.username,
			'words': sentence.words,
		})

	conversation.reverse()

	response['success'] = True
	response['data'] = conversation

	return HttpResponse(json.dumps(response))


def _get_sentences(user1, user2):
	query1 = Q(recipient=user1) & Q(sender=user2)
	query2 = Q(recipient=user2) & Q(sender=user1)
	return chat.models.Sentence.objects.filter(query1 | query2).order_by('-timestamp')
