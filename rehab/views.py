import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

from .forms import RehabilitatorRegisterForm, LoginForm, PatientRegisterForm, ExerciseForm, ExerciseDataForm
from .models import Rehabilitator, Patient, Exercise, ExerciseData


def home_view(request):
    user = request.user
    template = 'telemedWebapp/base.html'
    # Check if user has a Rehabilitator profile
    profile = None
    is_rehabilitator = None
    is_patient = None

    if hasattr(user, 'rehabilitator'):
        profile = user.rehabilitator
        is_rehabilitator = True
        is_patient = False
    elif hasattr(user, 'patient'):
        profile = user.patient
        is_rehabilitator = False
        is_patient = True
    return render(request, template, {'user': request.user,
                                      'is_rehabilitator': is_rehabilitator,
                                      'is_patient': is_patient})


def register_rehabilitator(request):
    is_registration_page = True
    which_account = 'rehabilitator'
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        form = RehabilitatorRegisterForm(request.POST)
        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            rehabilitator = form.save(commit=False)
            rehabilitator.user = user
            rehabilitator.save()
            login(request, user)
            return redirect('telemedWebapp:home')
    else:
        user_form = UserCreationForm()
        form = RehabilitatorRegisterForm()
    return render(request, 'telemedWebapp/register.html', {'user_form': user_form,
                                                           'form': form,
                                                           'which_account': which_account,
                                                           'is_registration_page': is_registration_page})


def register_patient(request):
    is_registration_page = True
    which_account = 'patient'
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        form = PatientRegisterForm(request.POST)
        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            patient = form.save(commit=False)
            patient.user = user
            patient.save()
            login(request, user)
            return redirect('telemedWebapp:home')
    else:
        user_form = UserCreationForm()
        form = PatientRegisterForm()
    return render(request, 'telemedWebapp/register.html', {'user_form': user_form,
                                                           'form': form,
                                                           'which_account': which_account,
                                                           'is_registration_page': is_registration_page})


@csrf_protect
def login_user(request):
    is_login_page = True
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('telemedWebapp:home'))
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'telemedWebapp/login.html', {'form': form,
                                                        'is_login_page': is_login_page})


def logout_user(request):
    logout(request)
    return redirect('telemedWebapp:home')


def view_all_rehabilitators(request):
    user = request.user
    is_rehabilitator = None
    is_patient = None
    if hasattr(user, 'rehabilitator'):
        profile = user.rehabilitator
        is_rehabilitator = True
        is_patient = False
    elif hasattr(user, 'patient'):
        profile = user.patient
        is_rehabilitator = False
        is_patient = True
    else:
        return redirect('telemedWebapp:home')

    query = request.GET.get('q', '')
    if query:
        rehabilitators = Rehabilitator.objects.filter(
            Q(name__icontains=query) |
            Q(surname__icontains=query) |
            Q(expertise__icontains=query)
        ).order_by('expertise', 'name', 'surname')
    else:
        rehabilitators = Rehabilitator.objects.all().order_by('expertise', 'name', 'surname')

    paginator = Paginator(rehabilitators, 10)  # 1 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'rehabilitators': rehabilitators,
               'query': query,
               'page_obj': page_obj,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    # Pass the list of Rehabilitators to the template
    return render(request, 'telemedWebapp/view_all_rehabilitators.html', context)


# @login_required
# def view_particular_patients(request):
#     user = request.user
#     is_rehabilitator = True
#     is_patient = False
#
#     if is_rehabilitator:
#         profile = user.rehabilitator
#         user = request.user
#         rehabilitator = user.rehabilitator
#         query = request.GET.get('q', '')
#         patients = Patient.objects.filter(
#             Q(name__icontains=query) |
#             Q(surname__icontains=query) |
#             Q(sex__icontains=query),
#             rehabilitator=rehabilitator
#         ).order_by('name', 'surname')
#
#         paginator = Paginator(patients, 10)  # 1 items per page
#         page_number = request.GET.get('page')
#         page_obj = paginator.get_page(page_number)
#
#         context = {'patients': patients,
#                    'query': query,
#                    'page_obj': page_obj,
#                    'is_rehabilitator': is_rehabilitator,
#                    'is_patient': is_patient}
#
#         # Pass the list of Rehabilitators to the template
#         return render(request, 'telemedWebapp/view_particular_patients.html', context)
#     return redirect('telemedWebapp:home')


@login_required
def view_particular_patients(request):
    is_rehabilitator = True
    is_patient = False

    current_rehabilitator = Rehabilitator.objects.get(user=request.user)
    query = request.GET.get('q', '')
    patients = Patient.objects.filter(
        Q(name__icontains=query) |
        Q(surname__icontains=query) |
        Q(sex__icontains=query),
        rehabilitator=current_rehabilitator
    ).order_by('name', 'surname')

    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'patients': patients,
               'query': query,
               'page_obj': page_obj,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    return render(request, 'telemedWebapp/view_particular_patients.html', context)

@login_required
def my_account_view(request):
    user = request.user
    template = 'telemedWebapp/my_account.html'
    # Check if user has a Rehabilitator profile
    profile = None
    is_rehabilitator = None
    is_patient = None

    if hasattr(user, 'rehabilitator'):
        profile = user.rehabilitator
        is_rehabilitator = True
        is_patient = False
    elif hasattr(user, 'patient'):
        profile = user.patient
        is_rehabilitator = False
        is_patient = True
    else:
        return redirect('telemedWebapp:home')
    return render(request, template, {'profile': profile,
                                      'is_rehabilitator': is_rehabilitator,
                                      'is_patient': is_patient})


@login_required
def edit(request):
    user = request.user
    is_rehabilitator = None
    is_patient = None

    if hasattr(user, 'rehabilitator'):
        is_rehabilitator = True
        is_patient = False

    elif hasattr(user, 'patient'):
        print("patient")
        is_rehabilitator = False
        is_patient = True

    if is_rehabilitator:
        if request.method == 'POST':
            form = RehabilitatorRegisterForm(request.POST, instance=user.rehabilitator)
            if form.is_valid():
                form.save()
                return redirect('telemedWebapp:home')
        else:
            form = RehabilitatorRegisterForm(instance=user.rehabilitator)


        return render(request, 'telemedWebapp/edit.html', {'form': form,
                                                           'is_rehabilitator': is_rehabilitator,
                                                           'is_patient': is_patient})

    if is_patient:
        if request.method == 'POST':
            form = PatientRegisterForm(request.POST, instance=user.patient)
            if form.is_valid():
                form.save()
                return redirect('telemedWebapp:home')
        else:
            form = PatientRegisterForm(instance=user.patient)

        return render(request, 'telemedWebapp/edit.html', {'form': form,
                                                           'is_rehabilitator': is_rehabilitator,
                                                           'is_patient': is_patient})


@login_required
def add_exercise(request):
    is_rehabilitator = False
    is_patient = True
    if request.method == 'POST':
        form = ExerciseForm(request.POST)
        if form.is_valid():
            exercise_form = form.save(commit=False)
            exercise_form.patient = request.user.patient
            exercise_form.save()
            return redirect('telemedWebapp:home')
    else:
        form = ExerciseForm()
    return render(request, 'telemedWebapp/add_exercise.html', {'form': form,
                                                               'is_rehabilitator': is_rehabilitator,
                                                               'is_patient': is_patient})

# @login_required
# def add_exercise(request):
#     is_rehabilitator = False
#     is_patient = True
#     if request.method == 'POST':
#         exercise_form = ExerciseForm(request.POST, request.FILES)
#         exercise_data_form = ExerciseDataForm(request.POST, request.FILES)
#         if exercise_form.is_valid() and exercise_data_form.is_valid():
#             exercise = exercise_form.save()
#             exercise_data_file = request.FILES['exercise_data_file']
#             reader = csv.reader(exercise_data_file)
#             for row in reader:
#                 exercise_data = ExerciseData(exercise=exercise, time=row[0], reps=row[1], weight=row[2])
#                 exercise_data.save()
#             return redirect('view_exercises')
#     else:
#         exercise_form = ExerciseForm()
#         exercise_data_form = ExerciseDataForm()
#
#     context = {'exercise_form': exercise_form,
#                'exercise_data_form': exercise_data_form,
#                'is_rehabilitator': is_rehabilitator,
#                'is_patient': is_patient}
#
#     return render(request, 'telemedWebapp/add_exercise.html', context)


@login_required
def view_exercises(request):
    user = request.user
    is_rehabilitator = None
    is_patient = None
    patient = None

    if hasattr(user, 'rehabilitator'):
        is_rehabilitator = True
        is_patient = False

    elif hasattr(user, 'patient'):
        print("patient")
        is_rehabilitator = False
        is_patient = True

    if is_rehabilitator:
        patient_id = request.GET.get('patient_id')
        patient = Patient.objects.get(id=patient_id)

    if is_patient:
        patient = request.user.patient

    query = request.GET.get('q', '')
    exercises = Exercise.objects.filter(
        Q(date_of_exercise__icontains=query) |
        Q(type_of_exercise__icontains=query),
        patient=patient
    ).order_by('date_of_exercise', 'type_of_exercise')

    paginator = Paginator(exercises, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'exercises': exercises,
               'query': query,
               'page_obj': page_obj,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    # Pass the list of Exercises to the template
    return render(request, 'telemedWebapp/view_exercises.html', context)

