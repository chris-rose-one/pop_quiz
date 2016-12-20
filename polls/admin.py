import datetime
from django.contrib import admin, messages
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
		(None, {'fields': ['question_text', 'starting_time', 'running_time', 'remain_active', 'vote_limit', 'one_vote_only']}),
	]
	inlines = [ChoiceInline]

	list_display = ('question_text', 'starting_time')

	def save_model(self, request, *args, **kwargs):
		try:
			return super(QuestionAdmin, self).save_model(request, *args, **kwargs)
		except Exception as e:
			messages.set_level(request, messages.ERROR)
			self.message_user(request, e, messages.ERROR)

admin.site.register(Question, QuestionAdmin)
