import datetime
from django.db import models
from django.utils import timezone
from django.core import serializers

def get_active_poll():
		for question in Question.objects.all():
			if question.is_active(): return question
		else: return None

def time_rounded_down(dt=None):
	if dt == None:
		dt = timezone.now()
	return dt + datetime.timedelta(seconds = -dt.second + 1, microseconds = -dt.microsecond)

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	starting_time = models.DateTimeField('start time', default=timezone.now)
	running_time = models.IntegerField(default=15)
	remain_active = models.IntegerField(default=5)
	one_vote_only = models.BooleanField(default=False)
	vote_limit = models.IntegerField(default=150)

	class Meta:
		ordering = ('starting_time',)
		managed = False

	def __str__(self):
		return self.question_text

	def get_end_time(self):
		return self.starting_time + datetime.timedelta(minutes = (self.running_time + self.remain_active), seconds = -1)

	end_time = property(get_end_time)

	def is_active(self):
		if timezone.now() >= self.starting_time \
		  and timezone.now() <= self.get_end_time():
			return True
		else: return False

	def is_open(self):
		if  timezone.now() >= self.starting_time \
		  and timezone.now() <= (self.starting_time + datetime.timedelta(minutes = self.running_time)):
			for choice in self.choice_set.all():
				if choice.votes == self.vote_limit: return False
			else: return True

	def seconds_remaining(self):
		diff = (self.starting_time + datetime.timedelta(minutes = self.running_time)) - timezone.now()
		return diff.total_seconds()

	def ordered_list_choices(self):
		tmp_data = []
		for choice in self.choice_set.all():
			tmp_data.append({'id': choice.id, 'choice_text': choice.choice_text, 'votes': choice.votes})
		sorted_data = sorted(tmp_data, key=lambda k: k['id'])
		return sorted_data

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	def __str__(self):
		return self.choice_text