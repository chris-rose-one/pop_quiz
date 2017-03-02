from django.core.management.base import BaseCommand, CommandError
from polls.models import Question, get_active_poll
from channels.asgi import get_channel_layer
from channels.sessions import session_for_reply_channel
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
import time, datetime
import json

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
		last_active = None

		while True:

			question = get_active_poll()

			# poll inactive
			if not question:
				if active_question is not None:
					active_question = None
					last_active = timezone.now()
				elif last_active and timezone.now() >= (last_active + datetime.timedelta(minutes=5)):
					reply_channels = get_reply_channels()
					for channel in reply_channels:
						sessions = get_reply_channel_sessions(channel)
						if sessions['http'].get('poll_status') == True \
						  or sessions['http'].get('poll_status') == False:
							sessions['http']['loaded_question'] = None
							sessions['http']['poll_status'] = None
							sessions['http']['has_voted'] = False
							sessions['http'].save()
							channel_layer.send(channel, {"text": json.dumps({"poll_ended": True})})

			elif question:
				# poll closing
				if question == active_question and not question.is_open():
					reply_channels = get_reply_channels()
					for channel in reply_channels:
						sessions = get_reply_channel_sessions(channel)
						if sessions['http'].get('poll_status') == True:
							sessions['http']['poll_status'] = False
							sessions['http'].save()
							channel_layer.send(channel, {"text": json.dumps({"poll_closed": True})})

				# new poll starting
				elif not question == active_question:
					if active_question is not None:
						assert active_question.is_active(), "active poll conflict"

					active_question = question
					last_active = None
					print(active_question)
					reply_channels = get_reply_channels()
					for channel in reply_channels:
						sessions = get_reply_channel_sessions(channel)
						if sessions['http'].get('poll_status') == False \
						  or sessions['http'].get('poll_status') == None:
							sessions['http']['loaded_question'] = question.id
							sessions['http']['poll_status'] = True
							sessions['http']['has_voted'] = False
							sessions['http'].set_expiry(question.seconds_remaining() + 3600)
							sessions['http'].save()
							channel_layer.send(channel, {"text": json.dumps({"poll_opening": {
								"question_id": question.id,
								"question_text": question.question_text,
								"vote_limit": question.vote_limit,
								"one_vote_only": question.one_vote_only,
								"choices": question.ordered_list_choices(),
								"has_voted": sessions['http'].get('has_voted')
							}})})

			time.sleep(1)
