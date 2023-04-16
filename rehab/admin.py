from django.contrib import admin

from rehab.models import Rehabilitator, Patient, Exercise, ExerciseData

# Register your models here.

admin.site.register(Rehabilitator)
admin.site.register(Patient)
admin.site.register(Exercise)
admin.site.register(ExerciseData)
