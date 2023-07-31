from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from employee.models import *
from .forms import UserLogin, UserAddForm
from auth_helper import *
from graph_helper import *
from typing import Dict
import json


def changepassword(request: HttpRequest):
    if not request.user.is_authenticated:
        return redirect('/')
    """
	This view allows the authenticated user to change their password.
	"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            update_session_auth_hash(request, user)

            messages.success(
                request,
                'Password changed successfully',
                extra_tags='alert alert-success alert-dismissible show',
            )
            return redirect('accounts:changepassword')
        else:
            messages.error(
                request,
                'Error,changing password',
                extra_tags='alert alert-warning alert-dismissible show',
            )
            return redirect('accounts:changepassword')

    form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password_form.html', {'form': form})


def register_user_view(request: HttpRequest) -> HttpResponse:
    # This view handles user registration.
    if request.method == 'POST':
        form = UserAddForm(data=request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            username = form.cleaned_data.get('username')

            messages.success(
                request,
                'Account created for {0} !!!'.format(username),
                extra_tags='alert alert-success alert-dismissible show',
            )
            return redirect('accounts:register')
        else:
            messages.error(
                request,
                'Username or password is invalid',
                extra_tags='alert alert-warning alert-dismissible show',
            )
            return redirect('accounts:register')

    form = UserAddForm()
    dataset = dict()
    dataset['form'] = form
    dataset['title'] = 'register users'
    return render(request, 'accounts/register.html', dataset)


def login_view(request: HttpRequest) -> HttpResponse:
    """
    This view handles the user login.

    """
    login_user = request.user
    if request.method == 'POST':
        form = UserLogin(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user and user.is_active:
                login(request, user)
                if login_user.is_authenticated:
                    return redirect('dashboard:dashboard')
            else:
                messages.error(
                    request,
                    'Account is invalid',
                    extra_tags='alert alert-error alert-dismissible show',
                )
                return redirect('accounts:login')

        else:
            return HttpResponse('data not valid')

    dataset = dict()
    form = UserLogin()

    dataset['form'] = form
    return render(request, 'accounts/login.html', dataset)


# def user_profile_view(request):
# 	'''
# 	user profile view -> staffs (No edit) only admin/HR can edit.
# 	'''
# 	user = request.user
# 	if user.is_authenticated:
# 		employee = Employee.objects.filter(user = user).first()


# 		dataset = dict()
# 		dataset['employee'] = employee


# 		return render(request,'dashboard/employee_detail.html',dataset)
# 	return HttpResponse("Sorry , not authenticated for this,admin or whoever you are :)")


def logout_view(request: HttpRequest) -> HttpResponse:
    # This view handles user logout.
    logout(request)
    return redirect('accounts:login')


def users_list(request: HttpRequest) -> HttpResponse:
    # This view displays a list of all users.
    employees = Employee.objects.all()
    return render(
        request,
        'accounts/users_table.html',
        {'employees': employees, 'title': 'Users List'},
    )


def users_unblock(request, id):
    # This view unblocks a user (makes them active)
    user = get_object_or_404(User, id=id)
    emp = Employee.objects.filter(user=user).first()
    emp.is_blocked = False
    emp.save()
    user.is_active = True
    user.save()

    return redirect('accounts:users')


def users_block(request, id):
    # This view blocks a user (makes them inactive).
    user = get_object_or_404(User, id=id)
    emp = Employee.objects.filter(user=user).first()
    emp.is_blocked = True
    emp.save()

    user.is_active = False
    user.save()

    return redirect('accounts:users')


def users_blocked_list(request: HttpRequest) -> HttpResponse:
    # This view displays a list of all blocked users.
    blocked_employees = Employee.objects.all_blocked_employees()
    return render(
        request,
        'accounts/all_deleted_users.html',
        {'employees': blocked_employees, 'title': 'blocked users list'},
    )


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""
""" AZURE SSO
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""


def initialize_context(request: HttpRequest) -> Dict[str, Any]:
    # This function initializes the context for Azure SSO
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = []
        context['errors'].append(
            error
        )  # Appending the error to the list only when it's not None

    # The user key and the default value should be separated by a comma
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context


def sign_in(request: HttpRequest) -> HttpResponseRedirect:
    # This function initiates the Azure SSO sign in flow.
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)  # Redirect to the Azure sign-in page
    return HttpResponseRedirect(flow['auth_uri'])


def sign_out(request: HttpRequest) -> HttpResponseRedirect:
    # This function signs out the user from Azure SSO
    # Clear out the user and token
    remove_user_and_token(request)
    return HttpResponseRedirect(reverse('home'))


def get_or_create_user(user_id: str, request: HttpRequest, name=None) -> User:
    # This function retrieves a user, or creates one if the user doesn't exist.
    user = User.objects.filter(username=user_id).first()

    if not user:
        user = User(username=user_id, email=user_id, first_name=name)
        user.save()

    request.user = user
    request.session['user_id'] = user_id
    login(request, user)
    return user


def callback(request: HttpRequest) -> HttpResponseRedirect:
    # This function handles the callback from the Azure SSO sign in flow.
    # Make the token request
    result = get_token_from_code(
        request
    )  # Get the user's profile from graph_helper.py script
    print(result)
    user = get_user(result['access_token'])  # Store user from auth_helper.py script
    store_user(request, user)

    ## Get User Object
    get_or_create_user(
        user['mail'] if (user['mail'] != None) else user['userPrincipalName'],
        request,
        name=user['displayName'],
    )
    print(request.user)
    return redirect('dashboard:dashboard')


"""""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""
""" SuperUser
""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """""" """"""


class CreateSuperuserView(View):
    def get(self, request, *args, **kwargs):
        # Check that the user is authorized to create superusers.
        # Replace this check with your own authorization logic.
        if not request.user.is_superuser:
            return HttpResponse('Unauthorized', status=401)

        # Load superuser credentials from a JSON file.
        with open('LeaveMgmt-Django\src\superuser_credentials.json') as f:
            credentials = json.load(f)

        # Create the superuser if it doesn't exist.
        if User.objects.filter(username=credentials['username']).exists():
            return HttpResponse('Superuser already exists.')
        else:
            User.objects.create_superuser(
                username=credentials['username'],
                email=credentials['email'],
                password=credentials['password'],
            )
            return HttpResponse('Superuser created.')
