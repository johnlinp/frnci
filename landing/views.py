# -*- coding: utf8 -*-

import re
import csv
import json
from django.http import HttpResponse
from django.core.urlresolvers import reverse
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

	locals_ = models.Local.objects.all()

	for local in locals_:
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

	models.Local.objects.all().delete()
	models.SpeakLanguage.objects.all().delete()
	models.GoPlace.objects.all().delete()
	models.Personality.objects.all().delete()
	models.HasPersonality.objects.all().delete()
	models.Interest.objects.all().delete()
	models.HasInterest.objects.all().delete()
	models.Activity.objects.all().delete()
	models.DoActivity.objects.all().delete()

	language_strs = [
		'Chinese',
		'Taiwanese',
		'English',
		'Cantonese',
		'Japanese',
		'Korean',
		'Spanish',
		'French',
		'German',
		'Italian',
		'Portuguese',
		'Thai',
		'Vietnamese',
		'Malay',
	]

	place_strs = [
		'Taipei',
		'Taoyuan',
		'Hsinchu',
		'Miaoli',
		'Taichung',
		'Changhua',
		'Yunlin',
		'Chiayi',
		'Tainan',
		'Nantou',
		'Kaohsiung',
		'Pingtung',
		'Taitung',
		'Hualien',
		'Yilan',
		'Outlying Islands',
	]

	file_read = request.FILES['locals']
	reader = csv.reader(file_read)
	rows = [row for row in reader]

	rows.pop(0)
	rows.pop(0)

	for row in rows:
		local = models.Local()
		local.display_name_en = row[1]
		local.sex = 'F' if row[2] == '女生' else 'M'
		local.email_addr = row[38]
		local.cell_phone = row[39]
		local.save()

		for idx, language_str in enumerate(language_strs):
			if row[3 + idx]:
				language = models.Language.objects.get(name=language_str)
				speak_language = models.SpeakLanguage()
				speak_language.local = local
				speak_language.language = language
				speak_language.save()

		for idx, place_str in enumerate(place_strs):
			if row[18 + idx]:
				place = models.Place.objects.get(name=place_str)
				go_place = models.GoPlace()
				go_place.local = local
				go_place.place = place
				go_place.save()

		def insert_item(whole_str, main_model, relation_model, item_str):
			strs = re.split(r'、|，| |,', whole_str)
			for str_ in strs:
				str_ = str_.strip()
				if not str_:
					continue
				try:
					main_item = main_model.objects.get(name_zh_tw=str_)
				except main_model.DoesNotExist:
					main_item = main_model(name_en=str_, name_zh_tw=str_)
					main_item.save()
				relation_item = relation_model()
				relation_item.local = local
				setattr(relation_item, item_str, main_item)
				relation_item.save()

		insert_item(row[35], models.Personality, models.HasPersonality, 'personality')
		insert_item(row[36], models.Interest, models.HasInterest, 'interest')

		activities_str = row[37]
		activity = models.Activity(name_en=activities_str, name_zh_tw=activities_str)
		activity.save()
		do_activity = models.DoActivity()
		do_activity.local = local
		do_activity.activity = activity
		do_activity.save()

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


