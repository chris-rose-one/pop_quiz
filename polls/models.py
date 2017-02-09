import json
import datetime
from django.db import models
from django.utils import timezone
from django.core import serializers
from django.dispatch import receiver
from django.db.models.signals import pre_save

def get_active_poll():
		for question in Question.objects.all():
			if question.is_active(): return question
		else: return None

def is_time_slot_free(instance):
	def find_queue_index(queue, value):
		for i, d in enumerate(queue):
			if d.id == value: return i

	temp = list(Question.objects.all())

	for question in temp:
		if question.id == instance.id:
			question.starting_time = instance.starting_time
			break
	else: temp.append(instance)

	sorted_queue = sorted(temp, key=lambda k: k.starting_time)
	obj_index = find_queue_index(sorted_queue, instance.id)
	obj_before = None
	obj_after = None

	if obj_index is not 0: obj_before = sorted_queue[obj_index - 1]
	if obj_index < (len(sorted_queue) - 1): obj_after = sorted_queue[obj_index + 1]

	if(obj_before is not None and instance.starting_time <= obj_before.get_end_time()): raise Exception('clashed with object before')
	elif(obj_after is not None and instance.get_end_time() >= obj_after.starting_time): raise Exception('clashed with object after')

class Question(models.Model):
	question_text = models.CharField(max_length=200)
	starting_time = models.DateTimeField('start time', default=timezone.now)
	running_time = models.IntegerField(default=15)
	remain_active = models.IntegerField(default=5)
	one_vote_only = models.BooleanField(default=False)
	vote_limit = models.IntegerField(default=150)

	class Meta:
		ordering = ('-starting_time',)
		managed = False

	def __str__(self):
		return self.question_text

	def get_end_time(self):
		return self.starting_time + datetime.timedelta(minutes = (self.running_time + self.remain_active))

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

	def choices_as_json(self):
		tmp_data = []
		for choice in self.choice_set.all():
			tmp_data.append({'id': choice.id, 'choice_text': choice.choice_text, 'votes': choice.votes})
		sorted_data = sorted(tmp_data, key=lambda k: k['id'])
		return json.dumps(sorted_data)

class Choice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	choice_text = models.CharField(max_length=200)
	votes = models.IntegerField(default=0)

	def __str__(self):
		return self.choice_text

@receiver(pre_save, sender=Question)
def pre_save_handler(sender, instance, *args, **kwargs):
	is_time_slot_free(instance)