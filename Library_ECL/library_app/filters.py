import django_filters

# import  from models.py 
from .models import User, OuvrageInstance, Subscription, Bad_borrower, Loan

class OuvrageFilter(django_filters.FilterSet):

    author = django_filters.CharFilter(lookup_expr='icontains',label='Auteur')
    name = django_filters.CharFilter(lookup_expr='icontains',label='Titre')
    class Meta:
        model = OuvrageInstance
        fields = ['name','author','ref_type']