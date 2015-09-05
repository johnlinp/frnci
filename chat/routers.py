from django.contrib.auth.models import User
from swampdragon import route_handler
from swampdragon.permissions import LoginRequired
from swampdragon.route_handler import ModelRouter
from chat.models import Sentence
from chat.serializers import SentenceSerializer


class SentenceRouter(ModelRouter):
	route_name = 'sentence'
	serializer_class = SentenceSerializer
	model = Sentence
	permission_classes = [LoginRequired()]


	def get_object(self, **kwargs):
		return self.model.objects.get(pk=kwargs['id'])


	def get_query_set(self, **kwargs):
		return self.model.objects.all()


	def get_initial(self, verb, **kwargs):
		recipient = User.objects.get(pk=kwargs['recipient_id'])
		sender = self.connection.user
		return {
			'recipient': recipient,
			'sender': sender,
		}


	def get_subscription_contexts(self, **kwargs):
		if 'source' not in kwargs:
			return {}

		# FIXME: sender__id__eq and recipient__id__eq are broken
		if kwargs['source'] == 'from-me':
			return {
				'sender__id__gte': self.connection.user.pk,
				'sender__id__lte': self.connection.user.pk,
			}
		elif kwargs['source'] == 'to-me':
			return {
				'recipient__id__gte': self.connection.user.pk,
				'recipient__id__lte': self.connection.user.pk,
			}
		else:
			return {}


route_handler.register(SentenceRouter)

