import json
from channels import Group
from channels.sessions import channel_session
from channels.auth import http_session, channel_session_user, channel_session_user_from_http
from .models import Question, Choice

# Connected to websocket.connect
@http_session
@channel_session_user_from_http
def ws_connect(message):
	keys = []
	for key in message.http_session.keys():
		if key not in message.channel_session.keys():
			keys.append((key, message.http_session[key]))
	else:
		for key in keys:
			message.channel_session[key[0]] = key[1]
	Group("poll").add(message.reply_channel)

# Connected to websocket.receive
@channel_session_user
def ws_vote(message):
	print(message.channel_session.items())
	data = json.loads(message['text'])
	question = Question.objects.get(pk=data['question_id'])
	selected_choice = question.choice_set.get(pk=data['choice_id'])
	if question.is_open:
		if not selected_choice.votes >= question.vote_limit:
			if question.one_vote_only and message.channel_session['has_voted'] == False:
				message.channel_session['has_voted'] = True
				selected_choice.votes += 1
				selected_choice.save()
				Group("poll").send({"text": question.choices_as_json(),})
			elif not question.one_vote_only:
				selected_choice.votes += 1
				selected_choice.save()
				Group("poll").send({"text": question.choices_as_json(),})
			if selected_choice.votes == question.vote_limit:
				question.is_open = False
				question.save()

# Connected to websocket.disconnect
@channel_session_user
def ws_disconnect(message):
    Group("poll").discard(message.reply_channel)
