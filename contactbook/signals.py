from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contact, Person

@receiver(post_save, sender=Contact)
def create_person(sender, instance, created, **kwargs):
	if created:
		Person.objects.create(contact=instance, user=instance.user, name=instance.name, firstname=instance.firstname, birthday=instance.birthday)

@receiver(post_save, sender=Contact)
def save_person(sender, instance, **kwargs):
	instance.person.save()