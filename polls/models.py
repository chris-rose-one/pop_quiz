import json
import datetime
from django.db import models
from django.utils import timezone
from django.core import serializers

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	starting_time = models.DateTimeField('start time', default=timezone.now)
	running_time = models.IntegerField(default=15)
	remain_active = models.IntegerField(default=5)
	one_vote_only = models.BooleanField(default=False)
	vote_limit = models.IntegerField(default=150)

	class Meta:
		ordering = ('-starting_time',)

	def is_active(self):
		if timezone.now() >= self.starting_time \
		  and timezone.now() <= (self.starting_time + datetime.timedelta(minutes = (self.running_time + self.remain_active))):
			return True
		else: return False

	def is_open(self):
		if  timezone.now() >= self.starting_time \
		  and timezone.now() <= (self.starting_time + datetime.timedelta(minutes = self.running_time)):
			for choice in self.choice_set.all():
				if choice.votes == self.vote_limit: return False
			else: return True

	def choices_as_json(self):
		tmp_data = []
		for choice in self.choice_set.all():
			tmp_data.append({'id': choice.id, 'choice_text': choice.choice_text, 'votes': choice.votes})
		sorted_data = sorted(tmp_data, key=lambda k: k['id'])
		return json.dumps(sorted_data)

	def __str__(self):
		return self.question_text

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	def __str__(self):
		return self.choice_text
