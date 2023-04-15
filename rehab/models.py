from django.db import models
from django.contrib.auth.models import AbstractUser, User


class Rehabilitator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)

    expertise = models.CharField(max_length=30)

    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))

    location = models.CharField(max_length=30)
    street = models.CharField(max_length=60)
    house_number = models.CharField(max_length=10)
    local_number = models.CharField(max_length=10)
    entity_name = models.CharField(max_length=60)

    def __str__(self):
        return self.expertise + " " + self.name + " " + self.surname


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    rehabilitator = models.ForeignKey(Rehabilitator, on_delete=models.CASCADE, related_name='patients')

    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)

    sex = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')))
    birth_date = models.DateField(null=True)

    location = models.CharField(max_length=30)
    street = models.CharField(max_length=60)
    house_number = models.CharField(max_length=10)
    local_number = models.CharField(max_length=10)

    def __str__(self):
        return self.name + " " + self.surname



class Exercise(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='exercises')
    type_of_exercise = models.CharField(max_length=15, choices=(('Sit-ups', 'Sit-ups'), ('Jumping-jacks', 'Jumping-jacks')))
    date_of_exercise = models.DateTimeField(null=True)


class ExerciseData(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='exercises_data')
    time = models.FloatField()
    seconds_elapsed = models.FloatField()
    z = models.FloatField()
    y = models.FloatField()
    x = models.FloatField()
