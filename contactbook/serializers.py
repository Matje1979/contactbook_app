from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Contact, Person



class ContactSerializer(ModelSerializer):

	user = PrimaryKeyRelatedField(read_only=True)
	
	class Meta:	
	    model = Contact
	    fields = ['user','gender', 'firstname', 'name', 'birthday', 'phone', 'email', 'active']

class PersonSerializer(ModelSerializer):

	contact = ContactSerializer(read_only=True)

	class Meta:
	    model=Person
	    fields=['gender', 'firstname', 'name', 'birthday', 'active', 'nickname', 'contact']

