from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.db.models import F
import uuid # Required for unique book instances
from django.urls import reverse
from datetime import date


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, social_status, password=None):
        """
        Creates and saves a User with the given email, first_name, last_name, social_status
        and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            social_status=social_status,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, social_status, password=None):
        """
        Creates and saves a superuser with the given email, first_name, last_name, social_status
        and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            social_status=social_status,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    class Meta:
        verbose_name = "Utilisateur"

    SOCIAL_STATUS = (
        ('CH', 'Chômeur'),
        ('ET', 'Étudiant'),
        ('SR', 'Senior'),
        ('ML', 'Militaire'),
        ('AU', 'Autre'),
    )
    social_status = models.CharField(max_length=2, choices=SOCIAL_STATUS, default='AU')
    first_name = models.CharField(max_length=60, default='first_name')
    last_name = models.CharField(max_length=60, default='last_name')
    balance = models.IntegerField(default=0, verbose_name="Solde €")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'social_status',]

    def __str__(self):
        return self.email

    def get_firstname(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class OuvrageInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID pour cette version dans toute la biliothèque')
    author = models.CharField(max_length=100, verbose_name='Auteur')
    name = models.CharField(max_length=200, verbose_name='Titre')
    description = models.CharField(max_length=1000, verbose_name='Description')
    publish_date = models.DateField(verbose_name='Date de Publication')
    borrowable = models.BooleanField(default=True) 
    REF_TYPE = (
        ('BK', 'Livre'),
        ('RV', 'Revue'),
        ('CD', 'CD'),
        ('BD', 'BD'),
        ('DVD', 'DVD'),
    )
    ref_type = models.CharField(max_length=3, choices=REF_TYPE, default='BK',help_text='Type ouvrage')
    

    class Meta:
        verbose_name = "Ouvrage"

    def __str__(self):
        return self.name

    @property
    def is_overdue(self):
        if self.return_date and date.today() > self.return_date:
            return True
        return False

class Subscription(models.Model):

    class Meta:
        verbose_name = "Abonnement"

    beginning_date = models.DateField(default=timezone.now ,verbose_name="Date de début")
    ending_date = models.DateField(default=timezone.timedelta(weeks=52) + timezone.now(),verbose_name="Date de fin")
    #A priori le one-to-one accepte le one-to-zero : un client peut avoir un abonnement / un abonnement est forcément lié à un client
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="", verbose_name="Utilisateur")

    def __str__(self):
        return self.user.email

class Loan(models.Model):

    class Meta:
        verbose_name = "Emprunt"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="",verbose_name="Utilisateur")
    reference = models.ForeignKey(OuvrageInstance, on_delete=models.CASCADE, default="",verbose_name="Ouvrage")
    beginning_date = models.DateField(default=timezone.now,verbose_name="Date de début")
    ending_date = models.DateField(default=timezone.timedelta(days=30) + timezone.now(),verbose_name="Date de fin")
    returned = models.BooleanField(default = False,verbose_name="Retourné ?")


    # to keep in memory the last value of returned because we want to make an action when returned changes from False to True
    __original_returned = None

    def __init__(self, *args, **kwargs):
        super(Loan, self).__init__(*args, **kwargs)
        self.__original_returned = self.returned
        

    # override save method to apply penalties or add bad borrower
    def save(self, *args, **kwargs):

        if self.returned:
            if self.__original_returned!=self.returned:
                today = datetime.date.today()
                # apply penalties if the book is returned 3 days later
                if (today-datetime.timedelta(days=3))>self.ending_date:
                    self.user.balance -= abs((today - self.ending_date).days)
                    self.user.save()

                self.ending_date = datetime.date.today() #change ending date to today
                # add to bad borrowers if it is the third time he is late
                nb_lates = Loan.objects.filter(
                        user=self.user # find the user
                    ).filter(
                        ending_date__gt=F('beginning_date')+datetime.timedelta(days=30) # ref returned in late
                    ).filter(
                        beginning_date__gte=today-datetime.timedelta(weeks=52) # only last year borrowings
                    ).count()

                if nb_lates>=3:
                    # test if the user has already been a bad borrower
                    if Bad_borrower.objects.filter(user=self.user).exists():
                        bad_user = Bad_borrower.objects.get(user=self.user)
                        bad_user.ending_date = today+datetime.timedelta(weeks=101)

                    else :
                        bad_user = Bad_borrower.objects.create(user=self.user)
                    bad_user.save()
        
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.__original_returned = self.returned


    def __str__(self):
        return self.reference.name

class Bad_borrower(models.Model):

    class Meta:
        verbose_name = "Mauvais utilisateur"

    user = models.OneToOneField(User, on_delete=models.CASCADE, default="",verbose_name="Utilisateur")
    ending_date = models.DateField(default=timezone.timedelta(weeks=101) + timezone.now(),verbose_name="Date de fin")

    def __str__(self):
        return self.user.email

    # override save method to delete subscription when we add a bad_borrower
    def save(self, *args, **kwargs):
        
        # check if the user had a subscription
        if Subscription.objects.filter(user__email=self.user.email).exists():
            Subscription.objects.get(user__email=self.user.email).delete()

        super().save(*args, **kwargs)  # Call the "real" save() method.

# test
