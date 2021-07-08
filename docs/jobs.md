# Working with the job system
As part of the projet there is a job system build on top of python-rq(https://python-rq.org/) using redis as a job queue.
All logic and utils related to job execution is localted in the app `kas.worker` app.
Each job is represented by an instance of the `worker.Job` model that is used to track progress and state (status of the job).

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
