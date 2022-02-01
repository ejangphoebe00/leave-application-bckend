# my-flask-boilerplate
This is a flask-file structure boilerplate that can be used to develop simple flask APIs. <br>
It can be cloned and used for every new project with slight modification.

# Usage
## clone repo
git clone https://github.com/conradsuuna/my-flask-boilerplate.git


## add .env file
touch .env

copy contents from .env.example and paste them in .env

## create a virtual environment
python -m venv chosen_environment_name

## activate virtual environment
source chosen_environment_name/bin/activate (for MAC and Linux)

## install dependencies 
python -m pip install -r requirements.txt

## create database with any database service;
db_name

### flask db init
Creates a new migration repository.

### flask db migrate
Autogenerate a new revision file (Alias for 'revision...)

### flask db upgrade
Commit migration changes to the database.
<!-- flask db stamp head -->
<!-- flask db merge heads -->

## run project
python app.py
or
flask run
