from django.test import TestCase, Client
from contactbook.models import Person, Contact, AddressEntry
from .serializers import ContactSerializer, PersonSerializer
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.test import APIClient
from .views import ContactListView, ContactDetailView, ListAddressesView
from datetime import date, timedelta
import json

# Create your tests here.

class TestModels(TestCase):

    def setUp(self):
        self.contact1 = Contact.objects.create(gender="Male",name="Peric", firstname="Pera")

    def tearDown(self):
        pass

    def test_address_entry(self):
        pass
    
    def test_person_model(self):
        persons = Person.objects.all()
        person1 = Person.objects.first()
        self.assertIsInstance(person1, AddressEntry) #Check whether contact inherits from AddressEntry.
        self.assertEqual(len(persons), 1) #Check whether the Person instance gets created when Contact instance is created.
        self.assertEqual(self.contact1, person1.contact)

    def test_contact_model(self):
        #A Person will be created when a contact is created, there will be additional fields to populate in the person model. 
        contacts = Contact.objects.all()
        self.assertEqual((self.contact1.gender, self.contact1.name, self.contact1.firstname),("Male", "Peric", "Pera"))
        self.assertIsInstance(contacts.first(), AddressEntry) #Check whether contact inherits from AddressEntry.
        contacts_number = len(contacts)
        persons_number = len(Person.objects.all())
        self.assertEqual(contacts_number, persons_number)

class TestUrls(TestCase):
    
    def test_list_contacts_url_resolves(self):
        url = reverse('contact_list')
        print (resolve(url)) 
        self.assertEqual(resolve(url).func.view_class, ContactListView)


    def test_list_addresses_resolves(self):
        url = reverse('list_addresses')
        print (resolve(url)) 
        self.assertEqual(resolve(url).func.view_class, ListAddressesView)


    def test_create_contact_url_resolves(self):
        url = reverse('contact_list')
        print (resolve(url)) 
        self.assertEqual(resolve(url).func.view_class, ContactListView)
   

    def test_update_contact_url_resolves(self):
        url = reverse('contact_detail', args=[12])
        print (resolve(url)) 
        self.assertEqual(resolve(url).func.view_class, ContactDetailView)


    def test_delete_contact_url_resolves(self):
        url = reverse('contact_detail', args=[12])
        print (resolve(url)) 
        self.assertEqual(resolve(url).func.view_class, ContactDetailView)


class TestViews(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="Mike", email="mike@gmail.com", password="xyzish2o")

        contact_list = [
            ("Male","Doe", "John", "2000-10-02"), 
        ]

        self.contact1 = Contact.objects.create(
                               gender=contact_list[0][0], 
                               name=contact_list[0][1], 
                               firstname=contact_list[0][2],  
                               birthday=contact_list[0][3],
                               phone="555333",
                               email="doe@gmail.com",
                               user=self.user,
                               active=True
                               )

        self.person1 = Person.objects.get(contact=self.contact1)
        
        self.create_contact_url = reverse('contact_list') #No point making create for person because it is tied to the contact.
        self.list_contact_url = reverse('contact_list')
        self.list_person_url = reverse('person_list')
        self.update_contact_url = reverse('contact_detail', args=[self.contact1.id])
        self.update_person_url = reverse('person_detail', args=[self.person1.id])
        self.delete_contact_url = reverse('contact_detail', args=[self.contact1.id])
        self.delete_person_url = reverse('person_detail', args=[self.person1.id])
        self.address_list_url = reverse('list_addresses')
        
        self.token = Token.objects.get(user__username="Mike").__str__()

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION= "Token " + self.token)

    def tearDown(self):
        pass

    def test_list_contacts_with_authorization(self):
        
        contacts = Contact.objects.filter(user__username="Mike")

        serializer = ContactSerializer(contacts, many=True)

        response = self.client.get(self.list_contact_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data, serializer.data)

    def test_list_contacts_without_authorization(self):

        self.client.force_authenticate(user=None)
        contacts = Contact.objects.filter(user__username="Mike")

        serializer = ContactSerializer(contacts, many=True)

        response = self.client.get(self.list_contact_url)
        self.assertEqual(response.status_code, 401)

        self.assertNotEqual(response.data, serializer.data)

    def test_list_persons_with_authorization(self):
        
        persons = Person.objects.filter(contact__user__username="Mike")

        serializer = PersonSerializer(persons, many=True)

        response = self.client.get(self.list_person_url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data, serializer.data)

    def test_list_persons_without_authorization(self):
        
        self.client.force_authenticate(user=None)
        persons = Person.objects.filter(contact__user__username="Mike")

        serializer = PersonSerializer(persons, many=True)

        response = self.client.get(self.list_person_url)
        self.assertEqual(response.status_code, 401)

        self.assertNotEqual(response.data, serializer.data)

    def test_create_contact(self):
        
        self.data = {
            "gender":"Female", "birthday":"2020-02-03", "firstname": "Jane", "name": "Doe", "phone": "067666777", "email":"janedoe@gmail.com", "user": self.user.id, "active": True
        }

        response = self.client.post(self.create_contact_url, data=self.data)
        # import pdb
        # pdb.set_trace()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_contact(self):
        self.data = {
            "gender":"Male", "birthday":"2020-02-03", "firstname": "George", "name": "Heys", "phone": "067666777", "email":"janedoe@gmail.com", "user": self.user.id, "active": True
        }
        response = self.client.put(self.update_contact_url, data=self.data)
        # import pdb
        # pdb.set_trace()
        self.assertEqual(response.status_code, 200)

    def test_update_person(self):
        self.data = {
            "gender":"Female", "birthday":"2000-02-03", "nickname":"Neo", "firstname": "Georgina", "name": "Heys"
        }
        response = self.client.put(self.update_person_url, data=self.data)
        # import pdb
        # pdb.set_trace()
        self.assertEqual(response.status_code, 200)

    def test_delete_contact(self):

        response = self.client.delete(self.delete_contact_url)
        con = Contact.objects.first()

        self.assertFalse(con.active)

    def test_address_list_without_query_parameter(self):
        response = self.client.get(self.address_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), '<p>Please put the query parameter is_older_than into the url.</p>')

    def test_address_list_with_query_parameter(self):
        response = self.client.get(f'{self.address_list_url}?is_older_than=1')
        self.assertEqual(response.status_code, 200)
        # import pdb
        # pdb.set_trace()
        res = json.loads(response.content)
        days_passed = 1 * 365
        today = date.today()
        time_difference = timedelta(days=int(days_passed))
        contacts = Contact.objects.filter(user__username="Mike").filter(birthday__lt = today - time_difference)
        persons = Person.objects.filter(user__username="Mike").filter(birthday__lt = today - time_difference)
    
        self.assertEqual(len(res['Contacts']) + len(res['Persons']), len(contacts) + len(persons)) #Checking if response contains the same number of elements


  




