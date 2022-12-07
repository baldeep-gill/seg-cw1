# Team *Dromedary* Small Group project

## Team members
The members of the team are:
- *Syraj Alkhalil k21007329*
- *Baldeep Gill k21034937*
- *Harry Davis k21049391*
- *Qadir Ijaz Fernandez k21095034*
- *Muhsin Mohamed k21088331*

## Project structure
The project is called `msms` (Music School Management System).  It currently consists of a single app `lessons` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *<[enter URL here](URL)>*.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

*The above instructions should work in your version of the application.  If there are deviations, declare those here in bold.  Otherwise, remove this line.*

## Sources
The packages used by this application are specified in `requirements.txt`

- Clucker code base
- Django custom authentication docs https://docs.djangoproject.com/en/4.1/topics/auth/customizing/#authentication-backends
