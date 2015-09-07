Guide
=====

Contribution
------------
Follow these rules strictly

- Line should no exceed the 100 characters
- Use 4 spaces instead of a tab
- Each app, models and function should have comment
- Follow PEP8 code formatting
- Format source before committing


Staging Environment
-------------------
API service is deployed on staging server hosted at AWS. We currently don't have production
environment.

We have CI setup with semaphore.com, so you don't need to deploy there manually. Simply push the
code to Github and you're good to go.


Creating New App
----------------


Usage of Signals
----------------

Synchronous
^^^^^^^^^^^

Asynchronous
^^^^^^^^^^^^




Schedule Task
-------------
We don't use cron job to schedule task but we use Celery beat instead that serves same purpose.
So don't manually need to cron in server and management become easy.

Please read its documentation on how it works and how to configure the job
