from django.urls import path
#app
from . import views 

urlpatterns = [
    path('users/',views.ListUsers.as_view(),name ="list_of_users"),
    path('register/',views.UserRegistrationView.as_view(),name="register"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/',views.LogoutView.as_view(),name="logout"),
    path('change-password/',views.ChangePassword.as_view(),name="change password"),

    #city
    path('addcity/',views.CityCreateViewSet.as_view(),name="city"),
    path('listcity/',views.CityListViewSet.as_view(),name="list cities"),
    path('updatecity/<pk>/',views.CityUpdateViewSet.as_view(),name="update city"),
    path('deletecity/<pk>/',views.CityDestroyViewSet.as_view({'get': 'destroy'}),name="delete city"),

    #theater
    path('addtheater/',views.TheaterCreateViewSet.as_view(),name=" create theater"),
    path('listtheater/',views.TheaterListViewSet.as_view(),name = "list theater"),
    path('deletetheater/<int:pk>/',views.TheaterDestroyViewSet.as_view({'get':'destroy'}),name = "delete theater"),
    path('updatetheater/<int:pk>/',views.TheaterUpdateViewSet.as_view(),name="update theater"),
    
    #movie
    path('addmovie/',views.MovieCreateViewSet.as_view(),name=" create theater"),
    path('listmovie/',views.MovieListViewSet.as_view(),name = "list theater"),
    path('deletemovie/<int:pk>/',views.MovieDestroyViewSet.as_view({'get':'destroy'}),name = "delete theater"),
    path('updatemovie/<int:pk>/',views.MovieUpdateViewSet.as_view(),name="update theater"),
    
    #show
    path('addshow/',views.ShowCreateViewSet.as_view(),name='create show'),
    path('listshow/',views.ShowListviewSet.as_view(),name = "list show"),

    #seat
    path('viewseats/',views.ViewAllSeats.as_view(),name="adding seats"),

    #book my show
    path('bookticket/',views.BookMyshow.as_view({'get':'list'}),name = "book show"),
    path('viewbookings/',views.ViewBookings.as_view(),name = "all bookings"),

    #export data in excel 
    path('exportexcel/',views.ExportExcel.as_view(),name='export excel'),
    path('excel/theater/',views.ExcelTheater.as_view(),name="export excel theater"),
]