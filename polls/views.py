import json
import datetime
from django.utils import timezone
from django.shortcuts import render
from django.template import loader

from .models import Question, Choice, get_active_poll

def poll(request):
	question = get_active_poll()
	if question:
		if not question.id == request.session.get('loaded_question'):
			request.session['loaded_question'] = question.id
			request.session['has_voted'] = False
		request.session['poll_status'] = question.is_open()
		request.session.set_expiry(question.seconds_remaining())
		return render(request, 'polls/poll.html', {
			'question': question, 
			'choices': json.dumps(question.ordered_list_choices()), 
			'has_voted': request.session['has_voted']
		})
	else:
		return render(request, 'polls/poll.html', {
			'error_message': "There isn't a poll running at the moment!"})
