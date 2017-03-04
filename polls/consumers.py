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
	message.reply_channel.send({"accept": True})
	if message.http_session: message.channel_session['http_session_key'] = message.http_session.session_key
	Group("poll").add(message.reply_channel)

# Connected to websocket.receive
@channel_session
def ws_receive(message):
	data = json.loads(message['text'])
	http_session = SessionStore(session_key=message.channel_session.get('http_session_key'))
	question = Question.objects.get(pk=data.get('question_id'))

	assert isinstance(question, Question), "question does not exist"
	assert question.is_active(), "question is not active"

	if 'vote' in data:
		selected_choice = question.choice_set.get(pk=data.get('choice_id'))

		assert isinstance(selected_choice, Choice), "choice does not exist"

		if selected_choice.votes >= question.vote_limit or not question.is_open():
			Group("poll").send({"text": json.dumps({"poll_closed": True}),})
		elif question.one_vote_only and http_session.get('has_voted') == False:
			http_session['has_voted'] = True
			http_session['vote_choice'] = selected_choice.id
			http_session.save()
			selected_choice.votes += 1
			selected_choice.save()
			Group("poll").send({"text": json.dumps({"poll_update": question.ordered_list_choices()}),})
			message.reply_channel.send({"text": json.dumps({"vote_confirm": True}),})
		elif not question.one_vote_only:
			selected_choice.votes += 1
			selected_choice.save()
			Group("poll").send({"text": json.dumps({"poll_update": question.ordered_list_choices()}),})

	elif 'undo' in data:
		if question.one_vote_only == True and http_session.get('has_voted') == True:
			selected_choice = question.choice_set.get(pk=http_session['vote_choice'])

			assert isinstance(selected_choice, Choice), "choice does not exist"

			http_session['has_voted'] = False
			http_session['vote_choice'] = None
			http_session.save()
			selected_choice.votes -= 1
			selected_choice.save()
			Group("poll").send({"text": json.dumps({"poll_update": question.ordered_list_choices()}),})
			message.reply_channel.send({"text": json.dumps({"undo_confirm": True}),})


# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("poll").discard(message.reply_channel)
