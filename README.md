# sandbox-mgt
Data Science Sandbox's Management webapp

## Setup

A dev can install this code locally and run the server:

    git clone git@github.com:alphagov/sandbox-mgt.git
    mkvirtualenv sandbox-mgt
    cd sandbox-mgt/sandboxmgt
    pip install -r ../requirements.txt
    ./manage.py runserver


## Static assets (CSS, JS, images)

This application is built using [govuk_elements](https://github.com/alphagov/govuk_elements)
and [govuk_template](https://github.com/alphagov/govuk_template/).

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