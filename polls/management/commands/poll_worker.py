from django.core.management.base import BaseCommand, CommandError
from polls.models import Question, get_active_poll
from channels.asgi import get_channel_layer
from django.contrib.sessions.backends.db import SessionStore
from channels.sessions import session_for_reply_channel
import time, json

class Command(BaseCommand):
	def handle(self, *args, **options):

		def get_reply_channels():
			return channel_layer.group_channels('poll')

		def get_reply_channel_sessions(channel):
			channel_session = session_for_reply_channel(channel)
			http_session = SessionStore(session_key=channel_session.get('http_session_key'))
			return {
				"channel": channel_session,
				"http": http_session
			}

		CLEAN_INTERVAL = 60
		channel_layer = get_channel_layer()
		active_question = None

		clean = 0

		while True:
			if clean == CLEAN_INTERVAL:
				reply_channels = get_reply_channels()
				for channel in reply_channels:
					sessions = get_reply_channel_sessions(channel)
				clean = 0

			question = get_active_poll()
			
			# new poll may be starting
			if question and not question == active_question:
				assert active_question and active_question.is_active(), "active poll conflict"
				
				active_question = question
				print(active_question)
				reply_channels = get_reply_channels()
				for channel in reply_channels:
					sessions = get_reply_channel_sessions(channel)
					if sessions['http'].get('poll_status') == False:
						sessions['http']['poll_status'] = True
						sessions['http']['has_voted'] = False
						sessions['http'].save()
						
						channel_layer.send(channel, {"text": json.dumps({"poll_opening": {
							"question_id": question.id,
							"question_text": question.question_text,
							"vote_limit": question.vote_limit,
							"one_vote_only": question.one_vote_only,
							"choices": question.ordered_list_choices(),
							"has_voted": sessions['http'].get('has_voted')
						}})})

			# poll may be closing
			elif question and question == active_question and not question.is_open():
				reply_channels = get_reply_channels()
				for channel in reply_channels:
					sessions = get_reply_channel_sessions(channel)
					if sessions['http'].get('poll_status') == True:
						channel_layer.send(channel, {"text": json.dumps({"poll_closed": True})})
						sessions['http']['poll_status'] = False
						sessions['http'].save()

			# poll may be becoming inactive
			elif not question:
				if active_question is not None:
					active_question=None


			clean += 1
			time.sleep(1)
