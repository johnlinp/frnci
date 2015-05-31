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


class Language(models.Model):
	name = models.CharField(max_length=10)


class SpeakLanguage(models.Model):
	local = models.ForeignKey(Local)
	language = models.ForeignKey(Language)


class Country(models.Model):
	name = models.CharField(max_length=20)


class Area(models.Model):
	name = models.CharField(max_length=20)


class Place(models.Model):
	name = models.CharField(max_length=20)
	country = models.ForeignKey(Country)
	area = models.ForeignKey(Area)


class GoPlace(models.Model):
	local = models.ForeignKey(Local)
	place = models.ForeignKey(Place)


class Personality(models.Model):
	name_en = models.CharField(max_length=20)
	name_zh_tw = models.CharField(max_length=20)


class HasPersonality(models.Model):
	local = models.ForeignKey(Local)
	personality = models.ForeignKey(Personality)


class Interest(models.Model):
	name_en = models.CharField(max_length=20)
	name_zh_tw = models.CharField(max_length=20)


class HasInterest(models.Model):
	local = models.ForeignKey(Local)
	interest = models.ForeignKey(Interest)


class Activity(models.Model):
	name_en = models.CharField(max_length=200)
	name_zh_tw = models.CharField(max_length=200)


class DoActivity(models.Model):
	local = models.ForeignKey(Local)
	activity = models.ForeignKey(Activity)


