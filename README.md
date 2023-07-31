# Django-Python LMS


## To Setup Application:

1. Download the file and unzip.
2. Create a Virtual Environment and Activate it
3. Open your Terminal/Command Prompt on the project’s root folder
4. Install the Requirements: pip install -r requirements.txt.
5. Then, make database migrations: python manage.py makemigrations
6. python manage.py migrate
7. After a successful migration run the application: python manage.py runserver
8. To create a superusr vist [link](https://docs.djangoproject.com/en/1.8/intro/tutorial02/)


## To Setup Azure SSO funtionality:

1. Visit: [link](https://aad.portal.azure.com/)
2. Now login with your account or create an Azure account
3. Once logged in go to Applications and click on App registration
4. Build the app and set the redirect URL "http://localhost:8000/accounts/callback"
5. Save the Application (client) ID on a notepad
6. Now open Certificates & secrets and create a new Client Secrets
7. Save the Client Secret "Value" on the notepad
8. Now open the IDE and under src/oauth_settings.yml . Setup Application (client) ID and Client Secret "Value".







[![codecov](https://codecov.io/gh/UtkarshV09/DeepStrat-LMS/branch/main/graph/badge.svg?token=WMJ5R8AHJT)](https://codecov.io/gh/UtkarshV09/DeepStrat-LMS)


![pylint Score](https://mperlet.github.io/pybadge/badges/5.92.svg)
