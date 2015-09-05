from django.db import models
from django.contrib.auth.models import User
from swampdragon.models import SelfPublishModel
from chat.serializers import SentenceSerializer#, FooSerializer


class Sentence(SelfPublishModel, models.Model):
	sender = models.ForeignKey(User, related_name='sender')
	recipient = models.ForeignKey(User, related_name='recipient')
	words = models.CharField(max_length=256)
	timestamp = models.DateTimeField(auto_now=True)
	serializer_class = SentenceSerializer


class Connect(models.Model):
	user1 = models.ForeignKey(User, related_name='user1')
	user2 = models.ForeignKey(User, related_name='user2')

	def get_friend(self, user):
		if self.user1 == user:
			return self.user2
		if self.user2 == user:
			return self.user1
		raise Exception('Not relevent connect')
