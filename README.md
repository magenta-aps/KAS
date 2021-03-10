# KAS

## Docker based development environment

| container | description | port |
|----------|--------------|------|
|kas-web   | Container running the kas django project | 8000/tcp |
|postgres  | Postgresql container, shared between kas and selvbetjening | 5432/tcp |
|oneshot   | Container to generate and execute migrations, and unit tests |
|selvbetjening | Container running the self-service django project. | 8080/tcp |

All django containers are using gunicorn and is configured to serve static content in the development environment and
log everything to stdout/stderr, so you can check the logs using docker logs <container_name>.
Gunicorn is set to auto-realod on (python) code changes.

### Running the project
```bash
docker-compose up
```

If you add/change/remove a dependency from a requirements.txt you have to rebuild to image using:
```bash
docker-compose build
```

## settings
All configurable settings needs to be injected using environment variables beucase we want to re-use the same
dockerFiles for development and production, if a needed setting is not provided the container should Fail fast so any
mistakes can be discovered as part of the deployment. All configurable django settings are located in
dev-environment/kas.env and dev-environment/selvbetjening.env and can be overriden directly in docker-compose.yml
using the environment block.

#worker POC
open: http://localhost:8000/worker/
press a button, see stuff works

# Working with the eSkat integration

## eSkat development setup

By default the eSkat setup will use local mockup tables as a data source for eSkat data. These tables will automatically
be used instead of the ones in the eSkat database when importing data. The tables can be populated with mockup data
by running the `perl manage.py import_eskat_mockup_data` command.

## Connecting to the real eSkat database

By default a development environment does not have the neccessary information to connect to the eSkat database.
In order to connect an SSH tunnel must be created that allows accessing the database server and login and password
credentials must be provided.

The ssh tunnel can be created from the development host with the following command:

```
ssh -g -L16523:10.240.79.23:16523 kas@10.240.76.76
```

The password needed to for the SSH connection can be found in Bitwarden under the key
`KAS test: kas@10.240.76.76 / kas@nokastest01.dmz70.local`.

Once the SSH tunnel is created a login and password is needed. These should be set up in a `docker-compose.override.yml` dockerFiles
like this:

```yaml
version: "3.4"
services:
  kas-web:
    environment:
      - ESKAT_USER=username
      - ESKAT_PASSWORD=password
```

The username and password to use can be found in BitWarden under the key `KAS login til eSkat database (10.240.79.23)`.

This will allow using the `eskat.models.EskatModels.*` model classes to connect to and query the live eSkat database.

If `settings.ENVIRONMENT` is set to `production`, the real eSkat database will be used by default.

## Creating new job Types
To create a new job type you have to add (or re-use) a form located in worker forms (use MandtalImportJobForm as an example).
The form is going to allow the user to add input parameters and selecting the job type, e.g. the MandtalImportJobForm
allows the user to input a tax year to import from eskat.

Secondly we need to add the job to the job registry located in worker.job_registry.py.
The job_registry holds the label and a reference to the newly created form.
The key is used as an internal/systematic name for the job-type.

Thirdly we need to import and add the job function to the StartJobView (worker/views.py)
so the function can get passed to the schedule_job function.

### Writing the job function
When writing the job function you could use the job_decorator from worker/models.py to handle starting, fetching
and finishing the job. If you use the decorator the job function will take a single argument: **job** which is the job
instance stored in the database. If you need any input parameters for the job they are stored in the **arguments** field
on the job as a dictionary.

When you need to update the progress you simply set the **progress** field on the job (or use the method on the job class)
and save the job to persist it in the database. All result data, like how many items are imported/changed, can be stored
in the **result** field (JsonB) and then it is up to you to parse it and present it in the job_detail template that
takes a simple job instance as context.


If there are any exceptions raised while executing the job it will trigger the registered exception handler which logs
the traceback in the traceback file on the job and set the job to status 'failed'.

##Running the containers as you
Because we specify a hardcoded user and group i the docker file this causes issues when you are trying to generate
migrations and translations since the container is trying to write as an unknown user to the hosts filesystem.
To overcome this we can ask the container to run as your user since your user should be the owner of the source code 
for the project and should be able to write files to the mounted volumes. Because the local user aka your UID and GID
will be different from installation to installation we can create a docker-compose.override.yml with the current 
uid and gid. First obtain the UID and GID by using the id command which should output something like
```bash
uid=1000(mac) gid=1000(mac) groups=1000(mac) ....
```

Then we can crate a docker-compose.override.yml with the following content (using the obtained uid, gid).
```yaml
version: "3.4"
services:
  kas-web:
    user: "1000:1000" #uid:gid


  selvbetjening:
    user: "1000:1000"
```
