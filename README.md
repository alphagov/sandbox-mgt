# sandbox-mgt

Data Science Sandbox's Management webapp

# Project Configuration

Make sure you have these environment variables set before running the project:

```
export HTTP_USERNAME='yourusername'
export HTTP_PASSWORD='yourpassword'
```

## Environment variables on the PAAS

Check existing environment variables:

```
cf env sandbox-mgt
```

Set environment variables on PAAS:

```
cf set-env sandbox-mgt HTTP_USERNAME ENV_VAR_VALUE
cf set-env sandbox-mgt HTTP_PASSWORD ENV_VAR_VALUE
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


## Static assets (CSS, JS, images)

This application is built using [govuk_elements](https://github.com/alphagov/govuk_elements)
and [govuk_template](https://github.com/alphagov/govuk_template/).

### Editing styles

Styles are generally edited in this Sass file:

    sandboxmgt/assets/scss/main.scss

which imports govuk_elements (which pulls in govuk-template). You can override variables before the import. You can override the styles themselves after the import.

Once it is edited, you need to recompile the styles (see next section) which will write the whole lot into:

    sandboxmgt/assets/css/main.css

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

4. Use gulp to compile the SCSS files:

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

To deploy to PaaS:

1. Get permissions. Dan needs to request the PaaS team adds you to the 'gds-data-science' org. Then Dan or sandbox team need to add you to the sandbox-dev space.

2. Login and target the dev box (or staging/production in future):

       cf login -a api.cloud.service.gov.uk -u <YOUR-EMAIL-ADDRESS>
       cf target -s sandbox-dev

3. Deploy. You should be in the root dir of your clone of the sandbox-mgt repo. This command deploys whatever state your repo is currently in:

       cf push sandbox-mgt
