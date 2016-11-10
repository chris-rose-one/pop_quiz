import json
from channels import Group
from .models import Question, Choice

# Connected to websocket.connect
def ws_connect(message):
    Group("poll").add(message.reply_channel)

# Connected to websocket.receive
def ws_vote(message):
	data = json.loads(message['text'])
	question = Question.objects.get(pk=data['question_id'])
	selected_choice = question.choice_set.get(pk=data['choice_id'])
	if not selected_choice.votes >= question.vote_limit: 
		selected_choice.votes += 1
		selected_choice.save()
		Group("poll").send({"text": question.choices_as_json(),})

# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("poll").discard(message.reply_channel)