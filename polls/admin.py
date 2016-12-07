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
		'''
		if obj.is_active == True:
			for question in Question.objects.all():
				if question.is_active is True:
					question.is_active = False
					question.save()
		'''
		obj.save()

admin.site.register(Question, QuestionAdmin)
