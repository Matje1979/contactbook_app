from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.
    
GENDER_CHOICES=(
        ("Male", "Male"),
        ("Female", "Female")
    )

class AddressEntry(models.Model):
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="Female")
    name = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50)
    birthday = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True)
    active = models.BooleanField(default=True)
    # user = models.ForeignKey(User,on_delete=models.CASCADE) allows multiple users to register their own contacts

    class Meta:
        abstract=True

class Contact(AddressEntry):
    user=models.ForeignKey(User,on_delete=models.CASCADE, null=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, null=True, blank=True )
    email = models.EmailField(max_length=100, null=True)

    def __str__(self):
        return f'{self.firstname} {self.name} contact info'

class Person(AddressEntry):
    user=models.ForeignKey(User,on_delete=models.CASCADE, null=True)
    nickname = models.CharField(max_length=50) 
    contact = models.OneToOneField(Contact, on_delete=models.CASCADE)
    # name=contact.name
    # firstname=contact.firstname

    def __str__(self):
        return f'{self.contact} profile'  


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)