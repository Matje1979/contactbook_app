from django.shortcuts import render
from .models import Contact, Person
from .serializers import ContactSerializer, PersonSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from datetime import date, timedelta
from rest_framework.response import Response
from django.http import HttpResponse

# Create your views here.


class ContactListView(ListCreateAPIView):

    serializer_class = ContactSerializer

    # authentication_classes = [TokenAuthentication]
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user).filter(active=True) #List only active contacts

class ContactDetailView(RetrieveUpdateDestroyAPIView):
    
    serializer_class = ContactSerializer

    permission_classes = (IsAuthenticated,)
    
    lookup_field="id"

    def get_queryset(self):

        return Contact.objects.filter(user=self.request.user)
    
    #Delete function relies on perform_destroy function for actual deleting, so we need to modify this function to inactivate contact instead of deleting it.
    def perform_destroy(self, instance):
        instance.active=False
        instance.save()


class PersonListView(ListCreateAPIView):

    serializer_class = PersonSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Person.objects.filter(contact__user=self.request.user)


class PersonDetailView(RetrieveUpdateDestroyAPIView):
    
    serializer_class = PersonSerializer

    permission_classes = (IsAuthenticated,)

    lookup_field="id"

    def get_queryset(self):

        return Person.objects.filter(contact__user=self.request.user)


class ListAddressesView(APIView):

    
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        age = request.query_params.get('is_older_than')
        contact_list = []
        if age:
            days_passed = int(age) * 365
            today = date.today()
            time_difference = timedelta(days=int(days_passed))
            contacts = Contact.objects.filter(user=self.request.user).filter(birthday__lt = today - time_difference)
            persons = Person.objects.filter(user=self.request.user).filter(birthday__lt = today - time_difference)
            contact_serializer = ContactSerializer(contacts, many=True)
            person_serializer = PersonSerializer(persons, many=True)
        
            return Response({"Contacts": contact_serializer.data, "Persons": person_serializer.data})
        else:
            return HttpResponse("<p>Please put the query parameter is_older_than into the url.</p>")
