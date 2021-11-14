
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models import F
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.urls import reverse 
import datetime
from .models import OuvrageInstance,User, Subscription, Bad_borrower, Loan, MyUserManager

def dictfetchall(cursor):
    desc= cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
        ]


class OuvrageCreationForm(forms.ModelForm):
    """A form for creating new references."""
    pass

class ReferenceAdmin(admin.ModelAdmin):
    form = OuvrageCreationForm
    list_display = ('name',  'author', 'publish_date', 'ref_type','available_link')
    list_filter = ('name',  'author', 'publish_date', 'ref_type')

    #cursor=connection.cursor()
    #borrowed=dictfetchall(cursor.execute("SELECT library_app_loan.id, "+
    #   " library_app_loan.user_id, "+
    #    "library_app_loan.reference_id, "+
    #    "library_app_loan.beginning_date, "+
    #    "library_app_loan.ending_date, "+
    #    "library_app_loan.returned "+
    # "FROM library_app_loan "+
    # "INNER JOIN library_app_ouvrageinstance "+
    #     "ON (library_app_loan.user_id = library_app_ouvrageinstance.id) "+
    # "WHERE NOT library_app_loan.returned"))

    def available_link(self, ref):
        borrowed = Loan.objects.filter(Q(reference=ref) & Q(returned=False)).exists()

        if not borrowed and ref.borrowable:
            path = "admin:library_app_loan_add"
            url = reverse(path)
            return mark_safe("<a href='{}'>Emprunter</a>".format(url))
        else :
            return ('Non disponible')

    available_link.short_description = 'Disponibilité'

# a form to create a subscription
class SubscriptionCreationForm(forms.ModelForm):
    """A form for creating new subscriptions."""

    # a field to be sure that the admin has been paid by the user
    payment = forms.BooleanField (label="L'utilisateur a-t-il bien payé?",required=True)

    # validation of all fields
    def clean(self):
        cleaned_data = super().clean()

        user = cleaned_data.get("user")
        
    # cursor=connection.cursor()
    # bad_borrowers=dictfetchall(cursor.execute("SELECT library_app_bad_borrower.email "+
    #    " FROM library_app_bad_borrower "+
    #     "WHERE library_app_bad_borrower.ending_date=DATE(NOW())"))

        # only users that aren't bad borrowers can have a subscription
        bad_borrowers = Bad_borrower.objects.filter(ending_date__gte=datetime.date.today()).values_list('user__email',flat=True)
        if str(user) in bad_borrowers :
            self.add_error('user', "Cet utilisateur est renseigné comme mauvais utilisateur")
        
        return cleaned_data

def subscription_cost(obj):
    
    # calculate subscription price
    price = 'Demi-tarif'
    if obj.user.social_status=='AU':
        price = 'Plein Tarif'
    
    if obj.user.social_status=='CH':
        price = 'Gratuit'

    return (price)

subscription_cost.short_description = 'Montant'

class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionCreationForm

    # The fields to be used in displaying the Subscription model.
    list_display = ('user',  'beginning_date', 'ending_date',subscription_cost)

    search_fields = ('user',)

    readonly_fields = ['beginning_date', 'ending_date',subscription_cost]

    actions = ['renew']

    # function to renew subscription
    def renew(modeladmin, request, queryset):
        for q in queryset:
            
            q.ending_date+=datetime.timedelta(weeks=52)
            q.save()
            messages.success(request, f"L'abonnement de %s a été renouvelé" % (q.user.email))

    renew.short_description = "Renouveler les abonnements"

    def response_change(self, request, obj):
        if "_renew" in request.POST:
            # do whatever you want the button to do
            obj.ending_date+=datetime.timedelta(weeks=52)
            obj.save()
            messages.success(request, f"L'abonnement de %s a été renouvelé" % (obj.user.email))
            return HttpResponseRedirect(reverse('admin:biblio_subscription_changelist'))  # stay on the same detail page
        return super().response_change(request, obj)

# to add a subscription info on user profil
class SubscriptionInline(admin.TabularInline):
    model = Subscription 
    readonly_fields = ["ending_date", "beginning_date"]

    def has_delete_permission(self, request, s):
        return False


######### Loan ###########

class LoanCreationForm(forms.ModelForm):
    """A form for creating new loan. Includes all the required
    fields"""

    class Meta:
        model = Loan
        fields = '__all__'
        #exclude = ('returned',)

    # only available reference
    # cursor=connection.cursor()
    # cursor.execute('SELECT library_app_ouvrageinstance.id, '+ 
    #                     'library_app_ouvrageinstance.author, '+ 
    #                     'library_app_ouvrageinstance.name, '+
    #                     'library_app_ouvrageinstance.description, '+ 
    #                     'library_app_ouvrageinstance.publish_date, '+
    #                     'library_app_ouvrageinstance.borrowable, '+
    #                     'library_app_ouvrageinstance.ref_type '+
    #                 'FROM library_app_ouvrageinstance '+
    #                 'WHERE library_app_ouvrageinstance.borrowable')
    # available_ref = dictfetchall(cursor)



    available_ref = OuvrageInstance.objects.filter(Q(borrowable=True)).distinct()
    reference = forms.ModelChoiceField(queryset=available_ref,required=True)

    ###### we don't use it here to allow user to test our data ######
    # validation of beginning_date
    #def clean_beginning_date(self):

    #    date = self.cleaned_data["beginning_date"]

        # check if the beginning date is superioir to today
    #    today = datetime.date.today()
    #    if date<today:
    #        raise ValidationError(
    #                "La date de début d'emprunt doit être postérieure à la date du jour"
    #            )

    #    return date

    # validation of all fields
    def clean(self):
        
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        reference = cleaned_data.get("reference")
        beginning_date = cleaned_data.get("beginning_date")
        ending_date = cleaned_data.get("ending_date")

        #cursor=connection.cursor()
        # cursor.execute("SELECT library_app_user.email "+
        #                 "FROM library_app_subscription "+
        #                 "WHERE library_app_subscription.ending_date >= DATE(NOW())")
        #valid_subscriptions_users = dictfetchall(cursor)

        # check if the user has a subscription
        today = datetime.date.today()
        valid_subscriptions_users = Subscription.objects.filter(ending_date__gte=today).values_list('user__email',flat=True)
        
        if user.email not in valid_subscriptions_users:
            self.add_error('user',
                    "Cet utilisateur n'a pas d'abonnement à jour"
                )

        # check if the user can borrow this type of reference
        if reference.ref_type=='BK':
            # books borrowing by the user
            nb_books_not_returned = Loan.objects.filter(
                    user__email=user.email
                ).filter(
                    Q(returned=False) 
                    & 
                    Q(reference__ref_type='BK')
                ).count() 
            
            # check if is borrowing less than 3 books
            if nb_books_not_returned>=3:
                self.add_error('reference', "Cet utilisateur emprunte déjà 3 livres")
        else:
            # reviews borrowing by the user
            nb_reviews_not_returned = Loan.objects.filter(
                    user__email=user.email
                ).filter(
                    Q(returned=False)
                ).exclude(
                    Q(reference__ref_type='BK')
                ).count() 

            # check if is borrowing less than 2 reviews
            if nb_reviews_not_returned>=2:
                self.add_error('reference', "Cet utilisateur emprunte déjà 2 revues")

        # check if the ending_date is 30 days after beginning date
        if ending_date!=(datetime.timedelta(days=30)+beginning_date):
            self.add_error('ending_date', "La durée d'un emprunt est de 30 jours")

        return cleaned_data


class LoanAdmin(admin.ModelAdmin):
    # The form to add Subscription instances
    form = LoanCreationForm

    # The fields to be used in displaying the Borrowed model.
    list_display = ('reference', 'user_link', 'beginning_date', 'ending_date','returned')

    list_filter = ('user','returned')

    actions = ['return_loan']

    # function to return one or several selected references
    def return_loan(modeladmin, request, queryset):
        for q in queryset:
            # if not already returned
            if not q.returned:
                q.returned='True' #mark as returned
                q.save()

    return_loan.short_description = "Retourner les ouvrages sélectionnés"

    def user_link(self, loan):

        path = "admin:library_app_user_change"
        url = reverse(path,args=(loan.user.id,))
        return mark_safe("<a href='{}'>{}</a>".format(url,loan.user.email))

    user_link.short_description = 'Utilisateur'


# to add a user borrowings on user profil
class LoanInline(admin.TabularInline):
    model = Loan 
    fieldsets = [
        (None, {'fields': ["loan_link","beginning_date","ending_date","returned"]})
        ]
    readonly_fields = ["loan_link","beginning_date","ending_date","returned"]

    def loan_link(self, loan):

        path = "admin:library_app_loan_change"
        url = reverse(path,args=(loan.id,))
        return mark_safe("<a href='{}'>{}</a>".format(url,loan.reference.name))

    loan_link.short_description = 'Ouvrage'

    def has_add_permission(self, request, s):
        return False

    def has_delete_permission(self, request, s):
        return False


################## Bad_borrower ####################

class Bad_borrowerAdmin(admin.ModelAdmin):
    list_display = ('user', 'ending_date')

class Bad_borrowerInline(admin.TabularInline):
    model = Bad_borrower
    readonly_fields = ["ending_date"]

    def has_delete_permission(self, request, s):
        return False
################## User ####################

# a form to create a new user
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'social_status')


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# a form to modify a user
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password',  'first_name', 'last_name', 'social_status', 'is_active', 'is_admin','balance')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

# class userAdmin to control what is print for this model
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email',  'first_name', 'last_name', 'social_status', 'is_admin','balance')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'first_name', 'last_name', 'social_status','balance')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','password1','password2','first_name', 'last_name', 'social_status','balance'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


    actions = ['pay_balance']
    inlines = [SubscriptionInline,LoanInline,Bad_borrowerInline]

    # function to return one or several selected references
    def pay_balance(modeladmin, request, queryset):
        for q in queryset:
            
            q.balance=0
            q.save()
            
    pay_balance.short_description = "Marquer que l'utilisateur à régler son solde"

admin.site.site_header = 'Bibliothèque - Admin'
admin.site.site_title = 'Bibliothèque - Admin'

# dire à Django quelle table afficher dans la partie admin
admin.site.register(OuvrageInstance, ReferenceAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Bad_borrower, Bad_borrowerAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)



