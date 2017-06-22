# sandbox-mgt

Data Science Sandbox's Management web app.


## Setup

A dev can install this repo's code locally and run the server:

```
git clone git@github.com:alphagov/sandbox-mgt.git
mkvirtualenv sandbox-mgt
cd sandbox-mgt/sandboxmgt
pip install -r ../requirements.txt
./manage.py runserver
```

## Deploy to PaaS

GOV.UK PaaS docs are here: https://docs.cloud.service.gov.uk/

To deploy to PaaS, set-up your account first.

### Set-up your account

1. Get permissions. Dan needs to request the PaaS team adds you to the 'gds-data-science' org. Then Dan or sandbox team need to add you to the 'sandbox-dev' space.

2. Login:

       cf login -a api.cloud.service.gov.uk -u <YOUR-EMAIL-ADDRESS>

### Deploy

1. Make sure you 'target' (deploy to) the right 'space'. It's probably 'sandbox-dev' now but in future it may be staging or production. The 'space' is saved in your environment. You might get asked which 'space' you want to target when you log-in. Otherwise use this command:

       cf target -s sandbox-dev

2. cd to the root dir of your clone of the sandbox-mgt repo.

       cd ~/sandbox-mgt

3. Deploy. This command deploys whatever state your local repo is currently in.

       cf push sandbox-mgt


## Password protection

On deployments, since this is an alpha, the site should be password protected. This is achieved by setting environment variables.

On PaaS, to view existing environment variables:

```
cf env sandbox-mgt
```

and to set them:
```
cf set-env sandbox-mgt HTTP_USERNAME <username>
cf set-env sandbox-mgt HTTP_PASSWORD <password>
```

To test password protection locally:
```
export HTTP_USERNAME='yourusername'
export HTTP_PASSWORD='yourpassword'
```
