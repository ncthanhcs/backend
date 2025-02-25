from django.contrib.auth.models import Permission, User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import datetime
class Movie(models.Model):
	title   	= models.CharField(max_length=200)
	genre  		= models.CharField(max_length=100)
	movie_logo  = models.FileField() 
	story_line  = models.CharField(max_length=500,default="sdf")
	date_public = models.DateField(default=datetime.date.today)
	mean_rate 	= models.IntegerField(default=1,validators=[MaxValueValidator(5),MinValueValidator(0)])
	def __str__(self):
		return self.title


class Myrating(models.Model):
	user   	= models.ForeignKey(User,on_delete=models.CASCADE) 
	movie 	= models.ForeignKey(Movie,on_delete=models.CASCADE)
	rating 	= models.IntegerField(default=1,validators=[MaxValueValidator(5),MinValueValidator(0)])
		