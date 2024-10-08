# aicon Runner

A program designed to monitor and evaluate submissions from aicon.

This version is a rewrite of the original aicon Runner, now utilizing Celery for better jobs management and performance.

## Dependencies

* Python >= 3.12
* Celery

## Usage

1. Duplicate the `example.env` file to create a new `.env` file.
2. Update the values in the `.env` file according to your aicon-web configuration.
3. Install the requirements:
```
pip install -r requirements.txt
```
4. Run watcher
```
python -m aicon_runner
```

You can also specify the number of concurrent processes using the following command:
```
python -m aicon_runner --concurrency 5
```

## Notes

* Ensure that the `AICON_AUTH_TOKEN` is associated with an admin user in the system.
* If `SLURM_VENV_DIRECTORY` is set, you must first run a single job (submission) to initialize the task environment. Submitting multiple jobs simultaneously may lead to race conditions during environment setup.
* `RUNNER_EVALUATOR_PATH` must be either a zip file or a valid Git URL pointing to a GitHub repository.

## Systemd Service

To configure and run the runner as a systemd service, follow these steps:

1. First, copy the `example.service` file to the appropriate systemd directory:
  ```bash
  cp example.service ~/.config/systemd/user/aicon-runner.service
  ```
2. Open the copied `aicon-runner.service` file and adjust the settings according to your specific requirements.
4. Verify your systemd service
  ```bash
  systemd-analyze verify ~/.config/systemd/user/aicon-runner.service
  ```
5. After making your modifications, you need to enable and start the service using the following commands:
  ```bash
  systemctl --user daemon-reload
  systemctl --user enable aicon-runner.service
  systemctl --user start aicon-runner.service
  ```
6. To ensure that the service is running correctly, check its status with:
  ```bash
  systemctl --user status aicon-runner.service
  ```

You can view the runner logs by using the following command:
```bash
journalctl --user -u aicon-runner.service
```

## Cron

If systemd is unavailable or linger isn't set, you can use cron to ensure that the runner is always alive.

### Steps:

1. **Copy the Script**
   First, copy `example.sh` to your desired directory. In this example, we'll use the home directory:
   ```bash
   cp example.sh $HOME/aicon-cron.sh
   ```

2. **Modify the Script**
   Customize `aicon-cron.sh` as needed for your specific requirements.

3. **Set Up Cron**
   Open the crontab for editing:
   ```bash
   crontab -e
   ```
   Add the following line to schedule the script to run every minute:
   ```
   * * * * * sh $HOME/aicon-cron.sh >> $HOME/aicon-cron.log 2>&1
   ```

### Viewing Logs

To check the log output from your script, use:
```bash
cat $HOME/aicon-cron.log
```
