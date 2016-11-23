import json
import datetime
from django.db import models
from django.utils import timezone
from django.core import serializers

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	vote_limit = models.IntegerField(default=150)
	one_vote_only = models.BooleanField(default=False)
	active = models.BooleanField(default=False)
	open = models.BooleanField(default=False)

	def choices_as_json(self):
		data = []
		for choice in self.choice_set.all():
			data.append({'id': choice.id, 'choice_text': choice.choice_text, 'votes': choice.votes})
		return json.dumps(data)

	def __str__(self):
		return self.question_text

	def save(self, *args, **kwargs):
		result = super(Question, self).save(*args, **kwargs)
		return result

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	def __str__(self):
		return self.choice_text
