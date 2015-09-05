from swampdragon.serializers.model_serializer import ModelSerializer


class SentenceSerializer(ModelSerializer):
	class Meta:
		model = 'chat.Sentence'
		publish_fields = ('recipient', 'sender', 'words')
		update_fields = ('recipient', 'sender', 'words')

	def serialize_sender_name(self, obj):
		return obj.sender.username
