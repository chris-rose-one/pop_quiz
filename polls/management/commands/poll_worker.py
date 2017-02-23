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

		channel_layer = get_channel_layer()
		active_question = None

		while True:
			question = get_active_poll()

			# new poll may be starting
			if question and not question == active_question:
				if active_question and active_question.is_active(): pass
				else:
					active_question = question
					print(active_question)

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
					pass



			time.sleep(1)
