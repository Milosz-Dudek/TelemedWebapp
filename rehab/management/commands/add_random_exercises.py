import random
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from rehab.models import Patient, Exercise, ExerciseData

patients = Patient.objects.all()


def random_timestamp():
    year = 2023
    month = random.randint(1, 12)

    if month in [4, 6, 9, 11]:
        days_in_month = 30
    elif month == 2:
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            days_in_month = 29
        else:
            days_in_month = 28
    else:
        days_in_month = 31

    day = random.randint(1, days_in_month)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    microsecond = random.randint(0, 999999)

    time = f"{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}.{microsecond:06}+00:00"
    return time


class Command(BaseCommand):
    help = "Adding N random rehabilitators"

    def add_arguments(self, parser):
        parser.add_argument("N", type=int)

    def handle(self, *args, **options):
        for i in range(options['N']):
            patient = random.choice(patients)
            if random.random() < 0.5:
                type_of_exercise = 'Jumping-jacks'
                csv_file_path = 'C:\\Users\\Miłosz\\Desktop\\Jumping-jacks.csv'
            else:
                type_of_exercise = 'Sit-ups'
                csv_file_path = 'C:\\Users\\Miłosz\\Desktop\\Sit-ups.csv'

            exercise = Exercise(
                patient=patient,
                type_of_exercise=type_of_exercise,
                date_of_exercise=random_timestamp()
            )

            exercise.save()
            print(exercise)

            @transaction.atomic
            def create_exercise_data(csv_file_path, commit=True, exercise=None):
                if csv_file_path:
                    df = pd.read_csv(csv_file_path)
                    exercise_data_list = []
                    for index, row in df.iterrows():
                        noise = np.random.normal(0, 1, 1)
                        exercise_data = ExerciseData(exercise=exercise,
                                                     time=row['time'],
                                                     seconds_elapsed=row['seconds_elapsed'],
                                                     z=row['z'] + noise,
                                                     y=row['y'] + noise,
                                                     x=row['x'] + noise)
                        exercise_data_list.append(exercise_data)

                    ExerciseData.objects.bulk_create(exercise_data_list)

                    if commit:
                        exercise.save()

                else:
                    raise ValueError('No CSV file provided')

                return exercise


            exercise_data = create_exercise_data(csv_file_path=csv_file_path, commit=True, exercise=exercise)
            exercise_data.save()
