from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

from .forms import RehabilitatorRegisterForm, LoginForm, PatientRegisterForm
from .models import Rehabilitator, Patient


# def home_view(request):
#     template = 'telemedWebapp/base.html'
#     return render(request, template, {'user': request.user})


def home_view(request):
    user = request.user
    template = 'telemedWebapp/base.html'
    # Check if user has a Rehabilitator profile
    profile = None
    is_rehabilitator = None

    if hasattr(user, 'rehabilitator'):
        profile = user.rehabilitator
        is_rehabilitator = True
    elif hasattr(user, 'patient'):
        profile = user.patient
        is_rehabilitator = False
    return render(request, template, {'user': request.user,
                                      'is_rehabilitator': is_rehabilitator})


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
    query = request.GET.get('q', '')
    if query:
        rehabilitators = Rehabilitator.objects.filter(
            Q(name__icontains=query) |
            Q(surname__icontains=query) |
            Q(expertise__icontains=query)
        )
    else:
        rehabilitators = Rehabilitator.objects.all()

    paginator = Paginator(rehabilitators, 2)  # 1 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'rehabilitators': rehabilitators,
               'query': query,
               'page_obj': page_obj}

    # Pass the list of Rehabilitators to the template
    return render(request, 'telemedWebapp/view_all_rehabilitators.html', context)


@login_required
def view_particular_patients(request):
    user = request.user
    rehabilitator = user.rehabilitator
    query = request.GET.get('q', '')
    patients = Patient.objects.filter(
        Q(name__icontains=query) |
        Q(surname__icontains=query) |
        Q(sex__icontains=query),
        rehabilitator=rehabilitator
    )

    paginator = Paginator(patients, 2)  # 1 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'patients': patients,
               'query': query,
               'page_obj': page_obj}

    # Pass the list of Rehabilitators to the template
    return render(request, 'telemedWebapp/view_particular_patients.html', context)


@login_required
def my_account_view(request):
    user = request.user
    template = 'telemedWebapp/my_account.html'
    # Check if user has a Rehabilitator profile
    profile = None
    is_rehabilitator = True

    if hasattr(user, 'rehabilitator'):
        profile = user.rehabilitator
        is_rehabilitator = True
    elif hasattr(user, 'patient'):
        profile = user.patient
        is_rehabilitator = False
    else:
        return redirect('telemedWebapp:home')
    return render(request, template, {'profile': profile,
                                      'is_rehabilitator': is_rehabilitator})


@login_required
def edit_rehabilitator(request, pk):
    rehabilitator = get_object_or_404(Rehabilitator, pk=pk)
    if request.method == 'POST':
        form = RehabilitatorRegisterForm(request.POST, instance=rehabilitator)
        if form.is_valid():
            form.save()
            return redirect('telemedWebapp:home')
    else:
        form = RehabilitatorRegisterForm(instance=rehabilitator)
    return render(request, 'telemedWebapp/edit.html', {'form': form})


@login_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientRegisterForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('telemedWebapp:home')
    else:
        form = PatientRegisterForm(instance=patient)
    return render(request, 'telemedWebapp/edit.html', {'form': form})
