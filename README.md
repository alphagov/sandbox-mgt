# sandbox-mgt

Data Science Sandbox's Management web app.


## Setup

A dev can install this repo's code locally and run the server:

### Postgres

Ensure you have PostgreSQL installed (tested with 9.6) installed. You can find more information for the different operating systems here: https://docs.djangoproject.com/en/1.10/ref/contrib/gis/install/postgis/
On OSX consider installing it with Brew or use the Postgres.app.

Once PostgreSQL is installed, create the database for this app:
```
createdb sandbox-mgt
```

### Python setup

```
git clone git@github.com:alphagov/sandbox-mgt.git
mkvirtualenv sandbox-mgt
cd sandbox-mgt/sandboxmgt
pip install -r ../requirements.txt
```

### Environment variables

Some configuration is done with environment variables. The simplest thing is to add them to your postactivate script e.g.:
```
vim ~/.virtualenvs/sandbox-mgt/bin/postactivate
```
The commands for configuring are:
```
export DATABASE_URL=postgres://localhost:5432/sandbox-mgt
export NOTIFY_API_KEY=<api-key>
export NOTIFY_EMAIL_TEMPLATE_ID=<template-id>
export NOTIFY_RECIPIENT_EMAIL=<your-own-email-address>
export AUTH0_DOMAIN=gds-sandbox.eu.auth0.com
export AUTH0_CLIENT_ID=<client-id>
export AUTH0_CLIENT_SECRET=<password>
export SANDBOX_DEPLOY_URL=http://localhost:7000/
```

Ask around the team to get these secrets.

On a development box, add:
```
export SANDBOX_MGT_DEBUG=True
```
otherwise the assets will not be served.

To test password protection, add:
```
export HTTP_USERNAME=<your-username>
export HTTP_PASSWORD=<your-password>
```

### Setup database

```
workon sandbox-mgt
./manage.py migrate
```

### Run local server

```
workon sandbox-mgt
./manage.py runserver
```


## Static assets (CSS, JS, images)

This application is built using [govuk_elements](https://github.com/alphagov/govuk_elements)
and [govuk_template](https://github.com/alphagov/govuk_template/).

### Editing styles

Styles are generally edited in this Sass file:

    sandboxmgt/assets/scss/main.scss

which imports govuk_elements (which pulls in govuk-template). You can override variables before the import. You can override the styles themselves after the import.

Once it is edited, you need to recompile the styles (see next section) which will write the whole lot into:

    sandboxmgt/assets/css/main.css

Note there are other compiled assets which have been simply copied into this repo and do not have a compilation pipeline set-up. e.g. govuk-template.css

### Re-compiling assets

Assets from those packages are already included in this repository.
Additionally the SCSS in `govuk_elements` is precompiled and the
resulting CSS is also included in the repository.

The reason assets are copied and pre-compiled here is to simplify
deployments.  That way, we're avoiding retrieving the `govuk_`
repositories, compiling the SASS (which would require installing
nodejs and npm), concatenating and minifying.

As a consequence, if changes are made to the javascript or SCSS files,
the developer will have to recompile locally. To do this:

1. Install Nodejs and npm:

        brew install node

2. Install gulp command-line tool globally:

        npm install --global gulp-cli

3. Install the node dependencies for this project:

        npm install

4. Clone product-page-example alongside this repo:

        cd ..
        git clone git@github.com:alphagov/product-page-example.git
        cd sandbox-mgt

5. Use gulp to compile the SCSS files:

        gulp styles
        gulp scripts

   or while you develop, it can compile them as you save them:

        gulp watchStyles
        gulp watchScripts

If a new version of the `govuk` packages is needed, you will have to
copy and compile them again, and add the resulting files in this
repository.


## Deploy to PaaS

GOV.UK PaaS docs are here: https://docs.cloud.service.gov.uk/

To deploy to PaaS, set-up your account first.

### Set-up your PaaS account

1. Get PaaS permissions. Dan needs to request the PaaS team adds you to the 'gds-data-science' org. Then Dan or sandbox team need to add you to the 'sandbox-dev' space.

2. Login:

       cf login -a api.cloud.service.gov.uk -u <YOUR-EMAIL-ADDRESS>


### Deploy the app

1. Make sure you 'target' (deploy to) the right 'space'. It's probably 'sandbox-dev' now but in future it may be staging or production. The 'space' is saved in your environment. You might get asked which 'space' you want to target when you log-in. Otherwise use this command:

       cf target -s sandbox-dev

2. cd to the root dir of your clone of the sandbox-mgt repo.

       cd ~/sandbox-mgt

3. Deploy. This command deploys whatever state your local repo is currently in.

       cf push sandbox-mgt


### Setup PostgreSQL service

This has to be done only the first time you deploy the app to a space.
NB this 'Free' type is not backed up - not for production use.

```
cf create-service postgres Free sandbox-mgt-pg
cf service sandbox-mgt-pg  # repeat until it's been created - 5-10 minutes
cf bind-service sandbox-mgt sandbox-mgt-pg
cf restage sandbox-mgt
cf service sandbox-mgt-pg  # check it says "Bound apps: sandbox-mgt"
```


### Environment variables configuration

On deployments, since this is an alpha, the site should be password protected. This is achieved by setting environment variables.

On PaaS, to view existing environment variables:

```
cf env sandbox-mgt
```

and to set them:
```
cf set-env sandbox-mgt HTTP_USERNAME <username>
cf set-env sandbox-mgt HTTP_PASSWORD <password>
cf set-env sandbox-mgt NOTIFY_API_KEY <api_key>
cf set-env sandbox-mgt NOTIFY_EMAIL_TEMPLATE_ID <template_id>
cf set-env sandbox-mgt NOTIFY_RECIPIENT_EMAIL <email_recipient>
cf set-env sandbox-mgt AUTH0_DOMAIN gds-sandbox.eu.auth0.com
cf set-env sandbox-mgt AUTH0_CLIENT_ID <client-id>
cf set-env sandbox-mgt AUTH0_CLIENT_SECRET <secret>
cf set-env sandbox-mgt SANDBOX_DEPLOY_URL https://deploy.sandbox.data-science.org.uk/
cf set-env sandbox-mgt SANDBOX_DEPLOY_USERNAME <username>
cf set-env sandbox-mgt SANDBOX_DEPLOY_PASSWORD <password>
```

### Admin users

This is how to make an 'admin' user in the sandbox-mgt web interface. They need to have logged into the web interface (i.e. with their GitHub account) already.

ssh into the box:
```
cf ssh sandbox-mgt
```

Activate the virtual environment:
```
export DEPS_DIR=/home/vcap/deps
for f in /home/vcap/app/.profile.d/*.sh; do source $f; done
```

Run the Django shell:
```
cd /home/vcap/app/sandboxmgt/
python manage.py shell
```

Find the user (here we use the email attached to the Github account) and give them staff & superuser permissions:
```
from django.contrib.auth.models import User
user = User.objects.get(email='david.read@hackneyworkshop.com')
user.is_staff = True
user.is_superuser = True
user.save()
```

* is_staff - whether can access the admin site
* is_superuser - needed to edit users

Now login to: https://sandbox-mgt.cloudapps.digital/admin/
* Create a group 'admin'
* Edit the user in question and add them to group 'admin'

They should now see the admin version of the nav menu.


## Auth0 account

Access to Auth0's gds-sandbox account is authorized by Dan

Log-in to https://manage.auth0.com/#/ via your google account.

Click on Client 'gds-sandbox' to see the settings for sandbox-mgt.


## Notify account

The Sandbox uses GOV.UK Notify to send emails: https://www.notifications.service.gov.uk/ .

Note that the NOTIFY_API_KEY cannot be obtained from the site and must be requested to one of the admins (Andrea Grandi or David Read).
