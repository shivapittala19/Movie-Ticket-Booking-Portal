import django_filters
from .models import Show,Seat

class ShowFilter(django_filters.FilterSet):
    theater = django_filters.CharFilter(field_name='theater__name', lookup_expr='icontains')
    time = django_filters.NumberFilter(field_name='time_id', lookup_expr='exact')
    cost = django_filters.NumberFilter(field_name='price', lookup_expr='exact')
    date = django_filters.DateFilter(field_name='time', lookup_expr='date')
    movie = django_filters.CharFilter(field_name='movie__movie_name',lookup_expr='icontains')
    
    class Meta:
        model = Show
        fields = ['theater', 'time', 'price', 'date','movie']

class ViewSeatsFilter(django_filters.FilterSet):
    seat_status =django_filters.CharFilter(field_name='booking_status',lookup_expr="icontains")
    show = django_filters.NumberFilter(field_name='show',lookup_expr="exact")


    class Meta:
        model = Seat
        fields = ['seat_status','show']



