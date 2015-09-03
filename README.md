# BuilderGiant

A marketplace for equipments. Buy/Sell/Rent everything.


# Technology Stack

* Python 2.7.x
* PostgreSQL 9.4.x
* Django 1.8
* Celery 3.1.x
* Redis 3.x
* Django REST Framework 3.0.x

## Mail

We are using http://www.mandrill.com/ for mail. All the mail templates are stored in their 
template engine (visit portal).

## Asynchronous Task

Celery is being used for asynchronous job and Celery Beat for schedule job. We use Redis as 
celery broker

## Static File Storage

Every static file that's being uploaded through API is stored in Cloudinary platform storage. We 
use their SDK to upload files.

## Logging and Exception Monitoring

We use Sentry (getsentry.com) for uncaught exception monitoring.

# Project Structure

It follow standard structure as Django project, contains the main project directory called 
`buildergiant` contains the settings and other configuration and various app directories.

Each app may contains the following module.

* `migrations` - Contains database migration to manipulate schemas that changes over the time
* `signals` - Contains the app related signals that is beind send on various events
* `apps.py` - General App configuration, usually contains the import of task module
* `messages.py` - Any kind of static messages like error message, info message is being stored 
here with their error code
* `models.py` - Standard modules to contains app related model and most of the business logic
* `notifications.py` - It should contain notification like email or push notification that is 
being sent to user on various events
* `serializers.py` - It should take care of serializing the input/output data to json and python
* `tasks.py` - It contains the function that receives signal and perform some tasks. It may also 
contains the function that is performed by Celery.
* `tests.py` - Holds various functional test of the app.
* `urls.py` - Contains the API endpoints urls
* `views.py` - Contains all the view set defined by DRF.

# Installation

This application is depends on few 3rd-party OS library and Python modules. 
If you're using `Ubuntu >= 14.04`, you can simply execute `osinstall.sh` to install OS packages.

To install Python dependencies, `pip` utility can be used.
 
    ./osinstall.sh
    pip install -r requirements.txt
    
## Installing Initial Schema

    ./manage.py migrate
    
## Initiate Default User Permissions
    
    ./manage.py syncperms
    
## Import Country Database

    ./manage.py cities --import=all
    
## Import US Sales Tax Database

    ./manage.py taxrates --import=all
    

# Running Tests

    ./manage.py test
