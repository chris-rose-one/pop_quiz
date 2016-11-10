from django.shortcuts import render
from django.template import loader

from channels import Group
from .models import Question, Choice

def poll(request):
	for question in Question.objects.all():
		if question.active == True:
			return render(request, 'polls/poll.html', {'question': question, 'choices': question.choices_as_json()})
	else:
		return render(request, 'polls/poll.html', {
			'error_message': "There isn't a poll running at the moment!"
		})