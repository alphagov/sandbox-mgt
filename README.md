# sandbox-mgt

Data Science Sandbox's Management webapp

# Project Configuration

Make sure you have these environment variables set before running the project:

```
export HTTP_USERNAME='yourusername'
export HTTP_PASSWORD='yourpassword'
```

## Setup

A dev can install this code locally and run the server:

```
git clone git@github.com:alphagov/sandbox-mgt.git
mkvirtualenv sandbox-mgt
cd sandbox-mgt/sandboxmgt
pip install -r ../requirements.txt
./manage.py runserver
```