# sandbox-mgt
Data Science Sandbox's Management webapp

## Setup

A dev can install this code locally and run the server:

    git clone git@github.com:alphagov/sandbox-mgt.git
    mkvirtualenv sandbox-mgt
    cd sandbox-mgt/sandboxmgt
    pip install -r ../requirements.txt
    ./manage.py runserver


## Deploy to PaaS

GOV.UK PaaS docs are here: https://docs.cloud.service.gov.uk/

To deploy to PaaS:

1. Get permissions. Dan needs to request the PaaS team adds you to the 'gds-data-science' org. Then Dan or sandbox team need to add you to the sandbox-dev space.

2. Login and target the dev box (or staging/production in future):

       cf login -a api.cloud.service.gov.uk -u <YOUR-EMAIL-ADDRESS>
       cf target -s sandbox-dev

3. Deploy. You should be in the root dir of your clone of the sandbox-mgt repo. This command deploys whatever state your repo is currently in:

       cf push sandbox-mgt
