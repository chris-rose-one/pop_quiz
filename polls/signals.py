from django.dispatch import receiver
from django.db.models.signals import pre_save
from .models import Question

@receiver(pre_save, sender=Question)
def pre_save_handler(sender, instance, *args, **kwargs):
	def find_queue_index(queue, value):
		for i, d in enumerate(queue):
			if d.id == value: return i

	temp = list(Question.objects.all())

	for question in temp:
		if question.id == instance.id:
			question.starting_time = instance.starting_time
			break
	else: temp.append(instance)

	sorted_queue = sorted(temp, key=lambda k: k.starting_time)
	obj_index = find_queue_index(sorted_queue, instance.id)
	obj_before = None
	obj_after = None

	if obj_index is not 0: obj_before = sorted_queue[obj_index - 1]
	if obj_index < (len(sorted_queue) - 1): obj_after = sorted_queue[obj_index + 1]

	if(obj_before is not None and instance.starting_time <= obj_before.get_end_time()): raise Exception('clashed with object before')
	elif(obj_after is not None and instance.get_end_time() >= obj_after.starting_time): raise Exception('clashed with object after')