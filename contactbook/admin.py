from django.contrib import admin

# Register your models here.

from contactbook.models import Person, Contact

admin.site.register(Person)
admin.site.register(Contact)