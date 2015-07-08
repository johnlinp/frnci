# -*- coding: utf8 -*-

import re
import csv
import json
import math
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.shortcuts import render
from django.shortcuts import redirect
from django.template.context_processors import csrf
import models


def home(request):
	context = {}
	context.update(csrf(request))
	if request.user.is_authenticated():
		try:
			access = request.user.accountaccess_set.all()[0]
		except IndexError:
			access = None
		else:
			client = access.api_client
			context['info'] = client.get_profile_info(raw_token=access.access_token)
	return render(request, 'index.html', context)


def locals_area(request, area_str):
	context = {}
	locals_info = []
	context['locals'] = locals_info

	show_full = request.user.is_authenticated()

	area = models.Area.objects.get(name=area_str)

	locals_ = models.Local.objects.all()
	for local in locals_:
		go_places = models.GoPlace.objects.filter(local=local)
		areas = [go_place.place.area for go_place in go_places]
		if area not in areas:
			continue
		local_info = local.to_info()
		locals_info.append(local_info)

		if not show_full and len(locals_info) >= 3:
			break

	return render(request, 'locals.html', context)


def locals_interest(request, interest_str):
	context = {}
	locals_info = []
	context['locals'] = locals_info

	show_full = request.user.is_authenticated()

	interest = models.Interest.objects.get_by_label(interest_str)
	locals_ = models.Local.objects.all()

	locals_ = models.Local.objects.all()
	for local in locals_:
		has_interests = models.HasInterest.objects.filter(local=local)
		interests = [has_interest.interest for has_interest in has_interests]
		if interest not in interests:
			continue
		local_info = local.to_info()
		locals_info.append(local_info)

		if not show_full and len(locals_info) >= 3:
			break

	return render(request, 'locals.html', context)


def locals_manage(request):
	if not request.user.is_staff:
		return redirect('/admin/')
	locals_info = []

	locals_ = models.Local.objects.all()
	for local in locals_:
		local_info = local.to_info()
		locals_info.append(local_info)

	return render(request, 'manage-locals.html', {'locals': locals_info})


def locals_import(request):
	if not request.user.is_staff or request.method != 'POST' or 'locals' not in request.FILES:
		return redirect(reverse('locals-manage'))

	_clear_all_locals()

	file_read = request.FILES['locals']
	reader = csv.reader(file_read)
	rows = [row for row in reader]

	rows.pop(0)

	paginator = Paginator(rows, 2)

	for idx in paginator.page_range:
		page = paginator.page(idx)
		main_row = page.object_list[0]
		en_row = page.object_list[1]

		name = main_row[1]
		sex = 'F'
		email = main_row[29]
		cell_phone = main_row[30]

		place_en_strs       = [place_en_str       for place_en_str       in en_row[4:8]     if place_en_str]
		interest_en_strs    = [interest_en_str    for interest_en_str    in en_row[8:12]    if interest_en_str]
		language_en_strs    = [language_en_str    for language_en_str    in en_row[12:16]   if language_en_str]
		personality_zh_strs = [personality_zh_str for personality_zh_str in main_row[16:20] if personality_zh_str]
		personality_en_strs = [personality_en_str for personality_en_str in en_row[16:20]   if personality_en_str]
		hobby_zh_strs       = [hobby_zh_str       for hobby_zh_str       in main_row[20:24] if hobby_zh_str]
		hobby_en_strs       = [hobby_en_str       for hobby_en_str       in en_row[20:24]   if hobby_en_str]

		activities_zh_str = main_row[24]
		activities_en_str = en_row[24]

		places_en_str = ' '.join(place_en_strs)
		place_en_strs = places_en_str.split()

		_add_single_local(name, sex, email, cell_phone, language_en_strs, place_en_strs, personality_zh_strs, personality_en_strs, interest_en_strs, hobby_zh_strs, hobby_en_strs, activities_zh_str, activities_en_str)

	return redirect(reverse('locals-manage'))


def pilot(request):
	result = {'success': False}
	email = request.GET.get('email', None)

	def is_valid_email(email):
		if '@' not in email:
			return False
		if email.startswith('@') or email.endswith('@'):
			return False
		return True

	if not email or not is_valid_email(email):
		return HttpResponse(json.dumps(result))

	try:
		old = models.Pilot.objects.get(email=email)
		result['success'] = True
		return HttpResponse(json.dumps(result))
	except models.Pilot.DoesNotExist:
		pass

	def get_client_ip(request):
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')
		return ip

	pilot = models.Pilot()
	pilot.email = email
	pilot.ip = get_client_ip(request)
	pilot.save()

	result['success'] = True

	return HttpResponse(json.dumps(result))


def fa(request):
	return render(request, 'fa.html')


def _clear_all_locals():
	models.Local.objects.all().delete()
	models.SpeakLanguage.objects.all().delete()
	models.GoPlace.objects.all().delete()
	models.Personality.objects.all().delete()
	models.HasPersonality.objects.all().delete()
	models.Hobby.objects.all().delete()
	models.HasHobby.objects.all().delete()
	models.Activity.objects.all().delete()
	models.DoActivity.objects.all().delete()
	models.HasInterest.objects.all().delete()


def _add_single_local(name, sex, email, cell_phone, language_en_strs, place_en_strs, personality_zh_strs, personality_en_strs, interest_en_strs, hobby_zh_strs, hobby_en_strs, activities_zh_str, activities_en_str):
	local = models.Local()
	local.display_name_en = name
	local.sex = sex
	local.email_addr = email
	local.cell_phone = cell_phone
	local.save()

	for language_str in language_en_strs:
		language = models.Language.objects.get(name=language_str)
		speak_language = models.SpeakLanguage()
		speak_language.local = local
		speak_language.language = language
		speak_language.save()

	for place_str in place_en_strs:
		place = models.Place.objects.get(name=place_str)
		go_place = models.GoPlace()
		go_place.local = local
		go_place.place = place
		go_place.save()

	for interest_str in interest_en_strs:
		print interest_str
		interest = models.Interest.objects.get(name_en=interest_str)
		has_interest = models.HasInterest()
		has_interest.local = local
		has_interest.interest = interest
		has_interest.save()

	for idx in range(len(personality_zh_strs)):
		personality = models.Personality()
		personality.name_en = personality_en_strs[idx][:20]
		personality.name_zh_tw = personality_zh_strs[idx][:19]
		personality.save()
		has_personality = models.HasPersonality()
		has_personality.local = local
		has_personality.personality = personality
		has_personality.save()

	for idx in range(len(hobby_zh_strs)):
		hobby = models.Hobby()
		hobby.name_en = hobby_en_strs[idx][:20]
		hobby.name_zh_tw = hobby_zh_strs[idx][:20]
		hobby.save()
		has_hobby = models.HasHobby()
		has_hobby.local = local
		has_hobby.hobby = hobby
		has_hobby.save()

	activity = models.Activity()
	activity.name_en = activities_en_str
	activity.name_zh_tw = activities_zh_str
	activity.save()
	do_activity = models.DoActivity()
	do_activity.local = local
	do_activity.activity = activity
	do_activity.save()

