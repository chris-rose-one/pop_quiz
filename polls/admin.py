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
		(None,			{'fields': ['question_text', 'vote_limit', 'one_vote_only', 'active', 'open']}),
	]
	inlines = [ChoiceInline]

	list_display = ('question_text', 'active')

	def save_model(self, request, obj, form, change):
		if obj.active == True:
			for question in Question.objects.all():
				if question.active is True:
					question.active = False
					question.save()
		obj.save()

admin.site.register(Question, QuestionAdmin)
