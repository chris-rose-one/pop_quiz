import datetime
from django.utils import timezone
from django.shortcuts import render
from django.template import loader

from .models import Question, Choice

def poll(request):
	def get_active_poll():
		for question in Question.objects.all():
			if question.is_active(): return question
		else: return False

	question = get_active_poll()
	if question:
		if not question.id == request.session.get('loaded_question'):
			request.session['loaded_question'] = question.id
			request.session['has_voted'] = False
		return render(request, 'polls/poll.html', {
			'question': question, 'choices': question.choices_as_json(), 'has_voted': request.session['has_voted']})
	else:
		return render(request, 'polls/poll.html', {
			'error_message': "There isn't a poll running at the moment!"})
