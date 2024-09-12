import json
import os
import traceback

from celery import shared_task
from .web import Aivle
from .utils import safe_filename
from . import config, slurm

STATUS_ERROR = 'E'
STATUS_DONE = 'D'

aivle = Aivle(config.aivle_url, auth=(config.aivle_username, config.aivle_password),
              force_https=config.aivle_force_https, verify=config.aivle_verify)

@shared_task
def evaluate(task_data: dict, submission_data: dict):
    response = aivle.job_run(submission_data)
    response.raise_for_status()

    # Define filepaths
    testsuite_path = os.path.join(config.runner_testsuites_path, f"{safe_filename(task_data['name'])}-{task_data['id']}.zip")
    submission_path = os.path.join(config.runner_submissions_path, f"{submission_data['id']}.zip")
    runner_kit_path = config.runner_runner_kit_path

    try:
        # Download packages
        response = aivle.download_package(task_data, testsuite_path)
        response.raise_for_status()
        response = aivle.download_package(submission_data, submission_path)
        response.raise_for_status()

        # Run
        result = slurm.run(
            testsuite_path,
            submission_path,
            runner_kit_path,
            time_limit = task_data["run_time_limit"] or config.slurm_run_time_limit,
            memory_limit = task_data["memory_limit"] or config.slurm_run_memory_limit,
            testsuite_id = task_data["id"],
            submission_id = submission_data["id"],
            partition = config.slurm_run_partition,
            base_dir = config.runner_runs_path,
            venv_base_dir = config.slurm_venv_directory,
            force = config.slurm_venv_force,
            use_slurm = config.slurm_enable,
            create_tmp_venv = config.slurm_venv_directory != "",
        )
        notes = result["test_cases"]
        submission_data['point'] = result['point']
        submission_data['status'] = STATUS_DONE
    except Exception as e:
        notes = {
            "error": {
                "type": str(type(e).__name__),
                "args": [str(earg) for earg in list(e.args)],
                # "trace": traceback.format_exc()
            }
        }
        submission_data['point'] = None
        submission_data['status'] = STATUS_ERROR

    submission_data['notes'] = json.dumps(notes)

    response = aivle.job_end(submission_data)
    assert response.ok, response
