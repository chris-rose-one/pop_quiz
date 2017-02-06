import json
from channels import Group
from channels.sessions import channel_session
from channels.auth import http_session
from django.contrib.sessions.backends.db import SessionStore
from .models import Question, Choice

# Connected to websocket.connect
@http_session
@channel_session
def ws_connect(message):
	if message.http_session: message.channel_session['http_session_key'] = message.http_session.session_key
	Group("poll").add(message.reply_channel)

# Connected to websocket.receive
@channel_session
def ws_vote(message):
	http_session = SessionStore(session_key=message.channel_session.get('http_session_key'))
	data = json.loads(message['text'])
	question = Question.objects.get(pk=data['question_id'])
	selected_choice = question.choice_set.get(pk=data['choice_id'])

	if question.is_active() and question.is_open():
		if not selected_choice.votes >= question.vote_limit:
			if question.one_vote_only and http_session['has_voted'] == False:
				http_session['has_voted'] = True
				http_session.save()
				selected_choice.votes += 1
				selected_choice.save()
				Group("poll").send({"text": question.choices_as_json(),})
			elif not question.one_vote_only:
				selected_choice.votes += 1
				selected_choice.save()
				Group("poll").send({"text": question.choices_as_json(),})

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("poll").discard(message.reply_channel)
