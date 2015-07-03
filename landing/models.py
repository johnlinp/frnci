import re
import hashlib
from django.utils.translation import ugettext
from django.utils.translation import get_language
from  django.core.exceptions import MultipleObjectsReturned
from django.db import models


class Local(models.Model):
	SEX = (
		('F', 'Female'),
		('M', 'Male'),
		('N', 'Rather not tell'),
	)

	display_name_en = models.CharField(max_length=30)
	sex = models.CharField(max_length=1, choices=SEX)
	email_addr = models.EmailField()
	cell_phone = models.CharField(max_length=20)

	def to_info(self):
		speak_languages = SpeakLanguage.objects.filter(local=self)
		go_places = GoPlace.objects.filter(local=self)
		has_personalities = HasPersonality.objects.filter(local=self)
		has_hobbies = HasHobby.objects.filter(local=self)
		do_activities = DoActivity.objects.filter(local=self)

		return {
			'name': self.display_name_en,
			'sex': dict(Local.SEX)[self.sex],
			'email': self.email_addr,
			'email_hash': hashlib.sha1(self.email_addr).hexdigest(),
			'cell_phone': self.cell_phone,
			'languages': [item.language for item in speak_languages],
			'places': [item.place for item in go_places],
			'personalities': [item.personality for item in has_personalities],
			'hobbies': [item.hobby for item in has_hobbies],
			'activities': [item.activity for item in do_activities],
		}


class Language(models.Model):
	name = models.CharField(max_length=10)

	def __str__(self):
		return ugettext(self.name).encode('utf8')

	def __repr__(self):
		return str(self)


class SpeakLanguage(models.Model):
	local = models.ForeignKey(Local)
	language = models.ForeignKey(Language)


class Country(models.Model):
	name = models.CharField(max_length=20)

	def __str__(self):
		return self.name.encode('utf8')

	def __repr__(self):
		return str(self)


class Area(models.Model):
	name = models.CharField(max_length=20)

	def __str__(self):
		return self.name.encode('utf8')

	def __repr__(self):
		return str(self)


class Place(models.Model):
	name = models.CharField(max_length=20)
	country = models.ForeignKey(Country)
	area = models.ForeignKey(Area)

	def __str__(self):
		return self.name.encode('utf8')

	def __repr__(self):
		return str(self)


class GoPlace(models.Model):
	local = models.ForeignKey(Local)
	place = models.ForeignKey(Place)


class Personality(models.Model):
	name_en = models.CharField(max_length=20)
	name_zh_tw = models.CharField(max_length=20)

	def __str__(self):
		if get_language() == 'zh-tw':
			return self.name_zh_tw.encode('utf8')
		return self.name_en.encode('utf8')

	def __repr__(self):
		return str(self)


class HasPersonality(models.Model):
	local = models.ForeignKey(Local)
	personality = models.ForeignKey(Personality)


class InterestManager(models.Manager):
	def get_by_label(self, label):
		selected = [interest for interest in self.all() if interest.to_label() == label]
		if len(selected) > 1:
			raise MultipleObjectsReturned()
		return selected[0]


class Interest(models.Model):
	name_en = models.CharField(max_length=20)
	name_zh_tw = models.CharField(max_length=20)
	objects = InterestManager()

	def __str__(self):
		if get_language() == 'zh-tw':
			return self.name_zh_tw.encode('utf8')
		return self.name_en.encode('utf8')

	def __repr__(self):
		return str(self)

	def to_label(self):
		name = self.name_en
		name = re.sub(r' & ', ' ', name)
		name = re.sub(' ', '-', name)
		name = name.lower()
		return name


class Hobby(models.Model):
	name_en = models.CharField(max_length=20)
	name_zh_tw = models.CharField(max_length=20)

	def __str__(self):
		if get_language() == 'zh-tw':
			return self.name_zh_tw.encode('utf8')
		return self.name_en.encode('utf8')

	def __repr__(self):
		return str(self)


class HasHobby(models.Model):
	local = models.ForeignKey(Local)
	hobby = models.ForeignKey(Hobby)


class HasInterest(models.Model):
	local = models.ForeignKey(Local)
	interest = models.ForeignKey(Interest)


class Activity(models.Model):
	name_en = models.CharField(max_length=200)
	name_zh_tw = models.CharField(max_length=200)

	def __str__(self):
		if get_language() == 'zh-tw':
			return self.name_zh_tw.encode('utf8')
		return self.name_en.encode('utf8')

	def __repr__(self):
		return str(self)


class DoActivity(models.Model):
	local = models.ForeignKey(Local)
	activity = models.ForeignKey(Activity)


class Pilot(models.Model):
	email = models.EmailField()
	ip = models.CharField(max_length=20)
	timestamp = models.DateTimeField(auto_now=True)
