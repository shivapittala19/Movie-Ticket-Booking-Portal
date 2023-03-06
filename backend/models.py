from django.db import models
from django.contrib.auth.models import AbstractUser, User ,PermissionsMixin
from datetime import datetime
from django.utils import timezone
from django.conf import settings

# Create your models here.


# class CustomUser(User):
#     is_theater_owner = models.BooleanField(default=False)
#     is_customer = models.BooleanField(default=True)
    
#     class Meta:
#         abstract =True
#         unique_together =("")



class City(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class Timings(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.start_time}-{self.end_time}'

class Theater(models.Model):
    name = models.CharField(max_length=20)
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    numberofscreens = models.IntegerField(default=1)
    address = models.CharField(max_length=200)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Movie(models.Model):
    MOVIE_TYPE = (
		('CHILDREN', 'CHILDREN'),
		('ADULT', 'ADULT'), 
		('FAMILY','FAMILY'),
		('NONE','NONE'),
        ('THRILLER','THRILLER'),
        ('COMEDY','COMEDY')
	)
    MOVIE_lANGUAGE = (
		('TELUGU', 'TELUGU'),
		('HINDI', 'HINDI'), 
		('ENGLISH','ENGLISH'),
		('TAMIL','TAMIL'),
        ('KANNADA','KANNADA'),
        
	)
    movie_name = models.CharField(max_length=200)
    language = models.CharField(max_length=24, choices=MOVIE_lANGUAGE)
    type = models.CharField(max_length=24, null=True, choices=MOVIE_TYPE, default=MOVIE_TYPE[3][0])
    movie_release_date = models.DateTimeField()
    movie_duration = models.PositiveIntegerField(help_text="Lenght of movie in minutes",default=180)
    
    def __str__(self):
        return self.movie_name
    
class Show(models.Model):
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE)
    capaticy = models.IntegerField(default=0)
    date = models.DateField()
    time = models.ForeignKey(Timings,on_delete=models.CASCADE)
    price =models.IntegerField(default=150)

    def __str__(self):
        return str(self.movie)


    
class Seat(models.Model):

    BOOKING_STATUS = (
		('BOOKED', 'BOOKED'),
		('AVAILABLE', 'AVAILABLE'), 
		('NOT_AVAILABLE','NOT_AVAILABLE')
	)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=5)
    booking_status = models.CharField(max_length=24, choices=BOOKING_STATUS, default=BOOKING_STATUS[1][0])
    
    
    def create_seat_instances(sender,instance,created,**kwargs):
        if created:
            for i in range(1,instance.capaticy+1):
                seat_number = i
                seat = Seat(show=instance,seat_number=seat_number)
                seat.save()
    models.signals.post_save.connect(create_seat_instances,sender=Show)
                
    def __str__(self):
        return self.seat_number
    


class Booking(models.Model):
    booking_id= models.CharField(max_length=20,unique=True)
    theater = models.ForeignKey(Theater,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie,on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    user = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    date = models.DateField()
    time = models.ForeignKey(Timings,on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=150)
    def __str__(self):
        return self.booking_id

