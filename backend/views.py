import string
import random
import json
import uuid
import xlwt
from datetime import datetime

#django 
from django.shortcuts import render
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
# from django_excel import make_response_from_query_sets
from django.http import HttpResponse
import django_filters.rest_framework
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError


#rest_framework
from rest_framework import permissions, generics,status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication,BaseAuthentication,SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

#app
from backend.serializers import UserSerializer,LoginSerializer,LogoutSerilizer, ShowSerializer
from backend.serializers import CitySerializer,TheaterSerializer,MovieSerializer,SeatSerializer
from backend.serializers import TimingsSerializer
from backend.serializers import BookingSerializer
from backend.models import City, Theater, Movie, Show , Seat, Booking,Timings
from backend.filters import ShowFilter,ViewSeatsFilter
from backend import permissions1
# Create your views here.



class ListUsers(APIView):
    permission_classes=[permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication]
    def get(self,request,format=None):
        usernames = [user.username for user in User.objects.all()]
        return Response(usernames)
    

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = request.data['password']
        if len(password)<=8:
            return Response({'message':'Password must have length atleast 8'})
        special= ['$', '#', '@', '!', '*']
        if not any(c in special for c in password):
            return Response({'message':'Password must contain at least one special character'})
        if not any(c.isupper() for c in password):
            return Response({'message':'Password must contain at least one uppercase letter'})
        if not any(c.islower() for c in password):
            return Response({'message':'Password must contain at least one lowercase letter'})
        if not any(c.isdigit() for c in password):
            return Response({'message':'Password must contain at least one digit'})
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()


    
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(username = serializer.validated_data['username'], password = serializer.validated_data['password'])

        if user:
            token,_ =Token.objects.get_or_create(user=user)
            login(request,user)
            return Response({'message':'logged in sucessful','user id':request.user.id,'token':token.key})  
        return Response(
            {'error': 'Invalid Credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerilizer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token,_= Token.objects.get_or_create(user=request.user)
        logout(request)
        return Response(data={"message":"logged out"},status=status.HTTP_200_OK)

class ChangePassword(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        current_password = request.data.get('current_password')
        new_password =request.data.get('new_password')
        if current_password and new_password:
        
            user=authenticate(username=request.user.username,password=current_password)

            if user is None:
                return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            if current_password == new_password:
                return Response({"message":"new password cannot be same as old password"},status=status.HTTP_400_BAD_REQUEST)
            
            if len(new_password)<=8:
                return Response({'message':'Password must have length atleast 8'})
            special= ['$', '#', '@', '!', '*']
            if not any(c in special for c in new_password):
                return Response({'message':'Password must contain at least one special character'})
            if not any(c.isupper() for c in new_password):
                return Response({'message':'Password must contain at least one uppercase letter'})
            if not any(c.islower() for c in new_password):
                return Response({'message':'Password must contain at least one lowercase letter'})
            if not any(c.isdigit() for c in new_password):
                return Response({'message':'Password must contain at least one digit'})
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Enter the Credentials'}, status=status.HTTP_400_BAD_REQUEST)


        

class TheaterCreateViewSet(generics.CreateAPIView):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        '''
        updating the user as a theater admin when he made as a admin in the post request
        '''
        data = serializer.data['admin']
        queryset = User.objects.get(id=data)
        queryset.is_theater_owner = True
        queryset.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        serializer.save()
   

class TheaterListViewSet(generics.ListAPIView):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter,filters.OrderingFilter,]
    search_fields = ['name','address','city__id']
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination

class TheaterDestroyViewSet(viewsets.ModelViewSet):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            queryset = Theater.objects.filter(admin=instance.admin_id) 
            data={"id":instance.id,"name":instance.name} 
            if queryset.count()==1:
                user = User.objects.get(id = instance.admin_id)
                user.is_theater_owner = False
                user.save()            
            self.perform_destroy(instance)
            return Response(data=data,status=status.HTTP_204_NO_CONTENT)


class TheaterUpdateViewSet(generics.UpdateAPIView):
    queryset = Theater.objects.all()
    serializer_class = TheaterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'


class CityCreateViewSet(generics.CreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]          

class CityListViewSet(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.SearchFilter,filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']

class CityDestroyViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            context ={"id":instance.id,"name":instance.name}
            self.perform_destroy(instance)
            return Response(data=context,status=status.HTTP_204_NO_CONTENT)
    
class CityUpdateViewSet(generics.UpdateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'



class MovieCreateViewSet(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]



class MovieListViewSet(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = [JWTAuthentication]
    filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    ordering_fields = '__all__'
    search_fields = ['movie_name','language','type','movie_duration']
    pagination_class = PageNumberPagination
    

class MovieDestroyViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = Movie
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
            instance = self.get_object()
            data={"id":instance.id,"name":instance.movie_name}
            self.perform_destroy(instance)
            return Response(data=data,status=status.HTTP_204_NO_CONTENT)


class MovieUpdateViewSet(generics.UpdateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'pk'

#show operations
class ShowCreateViewSet(generics.CreateAPIView):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions1.ISTheaterOwner]

    def get(self,request):
        queryset=Theater.objects.filter(admin=request.user)
        theater_name=[ data.name for data in queryset]
        return Response({'List of theaters where you are an admin':theater_name})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        theater = Theater.objects.get(name= serializer.validated_data['theater'])
        show = Show.objects.filter(date = serializer.validated_data['date'],time = serializer.validated_data['time'],theater=serializer.validated_data['theater'])
        if request.user != theater.admin:
            return Response(
               { "error":"You dont have access to add shows on another theater! Try adding shows on theaters  of your theater"},
                status = status.HTTP_400_BAD_REQUEST
            )
        if show.count() < theater.numberofscreens:
            self.perform_create(serializer)
        else:
            return Response(
                { 'message':f'This show at time  will excede number of screens in your theater! Add a show with differnt timings or upate the number of screens'}
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class ShowListviewSet(generics.ListAPIView):
    queryset = Show.objects.all()
    serializer_class = ShowSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filterset_class = ShowFilter
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination


class ViewAllSeats(generics.ListAPIView):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [permissions1.ISTheaterOwner]
    authentication_classes = [JWTAuthentication]
    # filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    filterset_class = ViewSeatsFilter
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination




class BookMyShow(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class BookMyshow(viewsets.ModelViewSet):
    queryset =Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = '__all__'
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        if request.data:
            theater_name = request.data['theater']
            movie_name = request.data['movie']
            date = request.data['date']
            time = request.data['time'].split('-')
        elif request.query_params:
            theater_name = request.query_params['theater']
            movie_name = request.query_params['movie']
            date = request.query_params['date']
            time = request.query_params['time'].split('-')
        else:
            return Response({"message":"pass the details of theater and movie that you are looking for"})  
        try:
            movie_id = Movie.objects.get(movie_name = movie_name).id
            theater_id = Theater.objects.get(name=theater_name).id
            time_id = Timings.objects.get(start_time=datetime.strptime(time[0],"%H::%M::%S").time(),end_time=datetime.strptime(time[1],'%H::%M::%S').time()).id
            show_id= Show.objects.get(movie=movie_id,theater=theater_id,date=date,time=time_id).id
        except (Theater.DoesNotExist, Show.DoesNotExist,Timings.DoesNotExist,Movie.DoesNotExist):
            return Response({'error': 'Invalid theater or show ID or Timings or Movie ID'}, status=400)
        
        seat_objects = Seat.objects.filter(show=show_id,booking_status='AVAILABLE')
        seat_serializer = SeatSerializer(seat_objects,many=True)
        return Response(seat_serializer.data)


    def post(self, request, *args, **kwargs):
        queryset = Seat.objects.all()
        theater = Theater.objects.all()
        serializer = self.get_serializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
       
        #validating where slected movie was available in the theater or not

        theater_id = serializer.validated_data['theater'].id
        movie_id  = serializer.validated_data['movie'].id
        date = serializer.validated_data['date']
        time_id = serializer.validated_data['time'].id
        show_queryset = Show.objects.filter(movie=movie_id,theater=theater_id)
        if not show_queryset:
            return Response({'errors':'This movie was not available in this theater select another theater and try again'})
        try:
            show_queryset=Show.objects.get(movie=movie_id,theater=theater_id,date=date,time=time_id)
        except(Show.DoesNotExist):
            return Response({'errors':'This movie was not availabe at this date or time! please select another timings'})
        
            
        #validating that selected seat instane exists in the show 
        # if serializer.validated_data['seat_number'].show_id != serializer.validated_data['show'].id:
        #     return Response ({"errors": 'selected seat is not ana intance of the show that you are selected'})
        
        try:

            seat_instance = queryset.get(
                seat_number=serializer.validated_data['seat_number'],
                show = show_queryset.id
                )
        except(Seat.DoesNotExist):
            return Response({'error':"seat matching query doesn't exists"})
        
        #checking the seat was availabe for booking or else reserved be someone else
        if seat_instance.booking_status != "AVAILABLE":
            return Response({'seat not available! Already booked'})
        
        #generating a random string for booking id
        booking_id = ''.join(random.choices(string.ascii_uppercase +string.digits, k=7))
        serializer.validated_data['booking_id'] = booking_id
        serializer.validated_data['user'] = request.user.username
        serializer.validated_data['email'] =request.user.email
        serializer.validated_data['price'] = show_queryset.price
        

        headers = self.get_success_headers(serializer.validated_data)
        serializer.save()

        #setting the status of booking as reserved when the ticket is booked
        seat_instance.booking_status = "RESERVED"
        seat_instance.save()

        booking = serializer.save()

        #send mail to the user when the ticket is booked
        send_ticket_email(booking)

        serializer_copy = serializer.data
        serializer_copy['booking_id'] = booking_id
        return Response(serializer_copy, status=status.HTTP_201_CREATED, headers=headers)
    

class ViewBookings(generics.ListAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

def send_ticket_email(booking):
        subject="Your ticket is booked"
        message ='Boking id : {}\n'\
                  'theater: {}\n'\
                  'movie: {}\n'\
                  'seat number : {}\n'\
                  'Date: {}\n'\
                  'Time : {}\n'\
                  'price : {}'.format(
            booking.booking_id,booking.theater.name,booking.movie.movie_name,booking.seat_number,
            booking.date,booking.time,booking.price
            )
        from_email ="shivapittala2001@gmail.com"
        recipient_list =["shivapittala2019@gmail.com"]
        send_mail(subject,message,from_email,recipient_list)

    
class ViewAvaliabilityOfSeats(generics.ListAPIView):
    queryset =Booking.objects.all()
    serializer_class  = BookingSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]



class ExportExcel(APIView):

    # authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self,equest):
        queryset = Booking.objects.all()
        headers =['id','Booking Id','Movie Name','Theater Name','Seat Number','City','Price','User','Email','Date','Time']
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="users.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users Data')

        row = 0
        col = 0 
        for header in headers:
            ws.write(row,col,header)
            col+=1

        row = 1
        for data in queryset:

            col=0
            ws.write(row,col,data.id)
            col+=1
            ws.write(row,col,data.booking_id)
            col+=1
            ws.write(row,col,data.movie.movie_name)
            col+=1
            ws.write(row,col,data.theater.name)
            col+=1
            ws.write(row,col,data.seat_number)
            col+=1
            ws.write(row,col,data.theater.city.name)
            col+=1
            ws.write(row,col,data.price)
            col+=1
            ws.write(row,col,data.user)
            col+=1
            ws.write(row,col,data.email)
            col+=1
            ws.write(row,col,data.date.strftime("%d-%m-%Y"))
            col+=1
            ws.write(row,col,data.time.start_time.strftime("%H:%M:%S") + "-" + data.time.end_time.strftime("%H:%M:%S"))

            row+=1
            
        wb.save(response)
        return response
    
class ExcelTheater(APIView):
    permission_classes =[permissions.IsAuthenticated]
    serializer_class = ShowSerializer
    def get(self,request):
        queryset = Show.objects.filter(theater=Theater.objects.get(admin=request.user.id).id)
        
        
        headers = ["id","Movie Name","Capacity","date","time","price","Number of booked seats"]
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="theater.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Users Data')

        row = 0
        col = 0 
        for header in headers:
            ws.write(row,col,header)
            col+=1

        row = 1
        for data in queryset:
            seat_instance =Seat.objects.filter(show=data.id)
            booked_seats = 0
            for seat in seat_instance:
                if seat.booking_status == "BOOKED":
                    booked_seats +=1
            col=0
            ws.write(row,col,data.id)
            col+=1
            ws.write(row,col,data.movie.movie_name)
            col+=1
            ws.write(row,col,data.capaticy)
            col+=1
            ws.write(row,col,str(data.date.day) + "/"+str(data.date.month) + "/"+str(data.date.year))
            col+=1
            ws.write(row,col,data.time.start_time.strftime("%H:%M:%S") + "-" + data.time.end_time.strftime("%H:%M:%S"))
            col+=1
            ws.write(row,col,data.price)
            col+=1
            ws.write(row,col,booked_seats)
            
            row+=1
        wb.save(response)
        return response

