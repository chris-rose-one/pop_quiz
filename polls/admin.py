import datetime
from django.contrib import admin
from .models import Choice, Question

class ChoiceInline(admin.TabularInline):
	model = Choice
	def get_extra(self, request, obj=None, **kwargs):
		extra = 3
		if obj and obj.choice_set.count() > extra:
			return 0
		elif obj: return extra - obj.choice_set.count()
		return extra

class QuestionAdmin(admin.ModelAdmin):
	fieldsets = [
		(None,			{'fields': ['question_text', 'starting_time', 'running_time', 'remain_active', 'vote_limit', 'one_vote_only']}),
	]
	inlines = [ChoiceInline]

	list_display = ('question_text', 'starting_time')

	def save_model(self, request, obj, form, change):
		def find_queue_index(queue, key, value):
			for i, d in enumerate(queue):
				if d.get(key) == value: return i

		temp = list(Question.objects.values())

		for question in temp:
			if question['id'] == obj.id:
				question['starting_time'] = obj.starting_time
				question['running_time'] = obj.running_time
				question['remain_active'] = obj.remain_active
				break
		else:
			temp.append({'id': obj.id,
			'starting_time': obj.starting_time,
			'running_time': obj.running_time,
			'remain_active': obj.remain_active
			})

		sorted_queue = sorted(temp, key=lambda k: k.get('starting_time'))
		obj_index = find_queue_index(sorted_queue, 'id', obj.id)
		try: obj_before = sorted_queue[obj_index - 1]
		except: obj_before = None
		try: obj_after = sorted_queue[obj_index + 1]
		except: obj_after = None
		if(obj_before and not obj.starting_time <= (obj_before['starting_time'] + datetime.timedelta(minutes = obj_before['running_time'] + obj_before['remain_active']))) \
		  or(obj_after and not (obj.starting_time + datetime.timedelta(minutes = obj.running_time + obj.remain_active)) >= obj_after['starting_time']):
			obj.save()

admin.site.register(Question, QuestionAdmin)
