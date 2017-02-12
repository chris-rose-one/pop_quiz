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
def ws_receive(message):
	data = json.loads(message['text'])
	http_session = SessionStore(session_key=message.channel_session.get('http_session_key'))
	if 'vote' in data:
		vote = data.get('vote')
		question = Question.objects.get(pk=vote.get('question_id'))
		selected_choice = question.choice_set.get(pk=vote.get('choice_id'))

		if question.is_active() and question.is_open():
			if not selected_choice.votes >= question.vote_limit:
				if question.one_vote_only and http_session['has_voted'] == False:
					http_session['has_voted'] = True
					http_session['vote_choice'] = vote.get('choice_id')
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
		undo = data.get('undo')
		question = Question.objects.get(pk=undo.get('question_id'))
		if question.is_active() and question.is_open() \
		  and question.one_vote_only == True and http_session['has_voted'] == True:
			selected_choice = question.choice_set.get(pk=http_session['vote_choice'])
			if selected_choice:
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
