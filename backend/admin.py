from django.contrib import admin
from .models import  Booking, Theater, Movie, Seat, Show
from .models import City,Timings
# Register your models here.

admin.site.register(Booking)
admin.site.register(Theater)
admin.site.register(Movie)
admin.site.register(Seat)
admin.site.register(Show)
admin.site.register(City)
admin.site.register(Timings)