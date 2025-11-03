from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self ,email, password=None ,**extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email ,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name= models.CharField(max_length=30)
    last_name=models.CharField(max_length=30)
    full_name=models.CharField(max_length=60) 
    is_staff = models.BooleanField(default=False)
    is_active=models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)
    date_joined= models.DateTimeField(default=timezone.now)
    date_of_birth = models.DateTimeField(null=True,blank=True)


    objects=CustomUserManager()

    USERNAME_FIELD=  "email" #email for login
    REQUIRED_FIELDS = ["first_name"]
    
    
    def get_full_name(self):
        full_name = self.first_name +" "+ self.last_name
        return full_name
    @property
    def age(self):
        if self.date_of_birth:
            return timezone.now().year - self.date_of_birth.year
        return None 
    
    
    def __str__(self):
        return f"{self.email}-({self.id}) "
    
    def save(self,*args,**kwargs):
        self.full_name= self.get_full_name()
        super().save(*args,**kwargs)

