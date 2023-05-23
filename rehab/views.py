import numpy as np
import seaborn as sns
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from io import BytesIO
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure
from scipy.signal import find_peaks
from django.http import JsonResponse

from .forms import RehabilitatorRegisterForm, LoginForm, PatientRegisterForm, ExerciseForm, ExerciseDataForm, \
    ExerciseFilterForm, PatientFilterForm, RehabilitatorFilterForm
from .models import Rehabilitator, Patient, Exercise, ExerciseData

sns.set_theme()


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


    rehabilitators = Rehabilitator.objects.all().order_by('expertise', 'name', 'surname')

    rehabilitator_filter_form = RehabilitatorFilterForm(request.GET)
    if rehabilitator_filter_form.is_valid():
        cd = rehabilitator_filter_form.cleaned_data
        if cd['name']:
            rehabilitators = rehabilitators.filter(name=cd['name'])
        elif cd['surname']:
            rehabilitators = rehabilitators.filter(surname=cd['surname'])
        elif cd['expertise']:
            rehabilitators = rehabilitators.filter(expertise=cd['expertise'])
        elif cd['location']:
            rehabilitators = rehabilitators.filter(location=cd['location'])
        elif cd['entity_name']:
            rehabilitators = rehabilitators.filter(entity_name=cd['entity_name'])

    paginator = Paginator(rehabilitators, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'rehabilitators': rehabilitators,
               'rehabilitator_filter_form': rehabilitator_filter_form,
               'page_obj': page_obj,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    # Pass the list of Rehabilitators to the template
    return render(request, 'telemedWebapp/view_all_rehabilitators.html', context)



@login_required
def view_particular_patients(request):
    is_rehabilitator = True
    is_patient = False

    current_rehabilitator = Rehabilitator.objects.get(user=request.user)
    patients = Patient.objects.filter(rehabilitator=current_rehabilitator).order_by('name', 'surname')

    # User submitted the form, process form data and update session variables
    patient_filter_form = PatientFilterForm(request.GET)
    if patient_filter_form.is_valid():
        cd = patient_filter_form.cleaned_data
        if cd['name']:
            patients = patients.filter(name=cd['name'])
        elif cd['surname']:
            patients = patients.filter(surname=cd['surname'])
        elif cd['sex']:
            patients = patients.filter(sex=cd['sex'])
        elif cd['birth_date_from'] and cd['birth_date_till']:
            patients = patients.filter(birth_date__range=(cd['birth_date_from'], cd['birth_date_till']))

    # Create the paginator using the filtered queryset
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {'patients': patients,
               'patient_filter_form': patient_filter_form,
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


def add_exercise(request):
    is_rehabilitator = False
    is_patient = True

    if request.method == 'POST':
        exercise_form = ExerciseForm(request.POST)
        exercise_data_form = ExerciseDataForm(request.POST, request.FILES)
        if exercise_form.is_valid() and exercise_data_form.is_valid():
            exercise = exercise_form.save(commit=False)
            exercise.patient = request.user.patient
            exercise.save()

            exercise_data = exercise_data_form.save(commit=False, exercise=exercise)
            exercise_data.save()

            return redirect('telemedWebapp:home')
    else:
        exercise_form = ExerciseForm()
        exercise_data_form = ExerciseDataForm()
    context = {'exercise_form': exercise_form,
               'exercise_data_form': exercise_data_form,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    return render(request, 'telemedWebapp/add_exercise.html', context)


@login_required
def edit_exercise(request):
    is_rehabilitator = False
    is_patient = True

    exercise_id = request.GET.get('exercise_id')
    exercise = Exercise.objects.get(id=exercise_id)

    if is_patient:
        if request.method == 'POST':
            exercise_form = ExerciseForm(request.POST, instance=exercise)
            if exercise_form.is_valid():
                exercise_form.save()
                return redirect('telemedWebapp:home')
        else:
            exercise_form = ExerciseForm(instance=exercise)

        return render(request, 'telemedWebapp/exercise_edit.html', {'exercise_form': exercise_form,
                                                                    'is_rehabilitator': is_rehabilitator,
                                                                    'is_patient': is_patient})


@login_required
def delete_exercise(request):
    is_rehabilitator = False
    is_patient = True

    exercise_id = request.GET.get('exercise_id')
    exercise = Exercise.objects.get(id=exercise_id)
    exercise_data = ExerciseData.objects.filter(exercise=exercise)

    if request.method == 'POST':
        if request.POST.get("confirm_delete"):
            exercise_data.delete()
            exercise.delete()
            return redirect('telemedWebapp:view_exercises')
        else:
            return redirect('telemedWebapp:view_exercises')

    return render(request, 'telemedWebapp/exercise_delete.html', {'exercise': exercise,
                                                                  'is_rehabilitator': is_rehabilitator,
                                                                  'is_patient': is_patient})


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
        is_rehabilitator = False
        is_patient = True

    if is_rehabilitator:
        if 'patient_id' in request.GET:
            patient_id = request.GET['patient_id']
            try:
                patient = Patient.objects.get(id=patient_id)
                request.session['patient_id'] = patient_id
            except Patient.DoesNotExist:
                pass
        elif 'patient_id' in request.session:
            patient_id = request.session['patient_id']
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                del request.session['patient_id']

    if is_patient:
        patient = request.user.patient
        patient_id = patient.id

    exercises = Exercise.objects.filter(patient=patient).order_by('date_of_exercise', 'type_of_exercise')

    exercise_filter_form = ExerciseFilterForm(request.GET)
    if exercise_filter_form.is_valid():
        cd = exercise_filter_form.cleaned_data
        if cd['type_of_exercise']:
            exercises = exercises.filter(type_of_exercise=cd['type_of_exercise'])
        elif cd['date_of_exercise_from'] and cd['date_of_exercise_till']:
            exercises = exercises.filter(
                date_of_exercise__range=(cd['date_of_exercise_from'], cd['date_of_exercise_till']))

    paginator = Paginator(exercises, 10)  # 10 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {'exercise_filter_form': exercise_filter_form,
               'exercises': exercises,
               'page_obj': page_obj,
               'is_rehabilitator': is_rehabilitator,
               'is_patient': is_patient}

    return render(request, 'telemedWebapp/view_exercises.html', context)


@login_required
def exercise_plot(request):
    user = request.user
    is_rehabilitator = None
    is_patient = None

    if hasattr(user, 'rehabilitator'):
        is_rehabilitator = True
        is_patient = False

    elif hasattr(user, 'patient'):
        is_rehabilitator = False
        is_patient = True

    exercise_id = request.GET.get('exercise_id')
    exercise = Exercise.objects.get(id=exercise_id)
    exercise_data = ExerciseData.objects.filter(exercise=exercise)
    x = np.array([data['x'] for data in exercise_data.values('x')])
    y = np.array([data['y'] for data in exercise_data.values('y')])
    z = np.array([data['z'] for data in exercise_data.values('z')])
    x = x[500:-500]
    y = y[500:-500]
    z = z[500:-500]

    time = np.linspace(0, np.max(x) - np.min(x), x.shape[0])

    z_peaks, _ = find_peaks(z, prominence=5, distance=100)

    y_peaks, _ = find_peaks(-y, prominence=30)

    fig = Figure(figsize=(12, 12), dpi=72)
    axs = fig.subplots(3, 1)

    axs[0].plot(time, x, '-r')
    axs[0].set_title('X-axis')
    axs[1].plot(time, y, '-g')
    axs[1].set_title('Y-axis')
    axs[1].set_ylabel('Acceleration [m/s$^{{\\mathregular{{2}}}}$]')
    axs[2].plot(time, z, '-b')
    axs[2].set_title('Z-axis')
    axs[2].set_xlabel('Time [s]')
    fig.tight_layout()

    buffer = BytesIO()
    canvas = FigureCanvasSVG(fig)
    canvas.print_figure(buffer)

    plot_data = buffer.getvalue().decode(settings.DEFAULT_CHARSET)

    context = {
        'exercise': exercise,
        'plot_data': plot_data,
        'is_rehabilitator': is_rehabilitator,
        'is_patient': is_patient,
        'sit_ups_count': z_peaks.shape[0],
        'jumping_jacks_count': (y_peaks.shape[0] - 1) // 2,
    }

    return render(request, 'telemedWebapp/exercise_plot.html', context)
