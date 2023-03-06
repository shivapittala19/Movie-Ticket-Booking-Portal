#django
from django.contrib.auth.models import User, Group
from django.db import models
#rest_framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator,UniqueTogetherValidator
#app
from backend.models import City, Theater, Movie, Seat, Show,Booking
from backend.models import Timings

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username','password','email','first_name','last_name']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class LogoutSerilizer(serializers.Serializer):
    pass


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
            queryset = City.objects.all(),
            fields = ['name']
            )
        ]


class TheaterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Theater
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Theater.objects.all(),
                fields= ['name','city']
            ),
            # UniqueValidator(
            #     queryset=Theater.objects.all(),
            #     fields = ['admin']
            # )      
        ]
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
            queryset=Movie.objects.all(),
            fields = ['movie_name']
            )
        ]

class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Show
        fields  = '__all__'
        validators = [
            UniqueTogetherValidator(
            queryset=Show.objects.all(),
            fields= ['movie','theater','time','date']
            )
        ] 




class SeatSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(help_text="enter the seat number within the capacity of the show seats")
    class Meta:
        model = Seat
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
            queryset= Seat.objects.all(),
            fields = ['show','seat_number']
            )
        ]

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields =['theater','movie','date','time','seat_number']

class TimingsSerializer(serializers.ModelSerializer):
    class Meat:
        model = Timings

        

