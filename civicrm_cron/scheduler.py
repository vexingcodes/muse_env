"""Periodically runs the CiviCRM jobs."""

import logging
import os
import signal
import sys

import apscheduler.schedulers.blocking
import requests

def sigterm_handler(signo, stack_frame):
    logging.info("sigterm_handler executed, %s, %s", signo, stack_frame)
    sys.exit(0)

def civicrm_cron():
    """Runs the CiviCRM jobs once."""
    logging.info(requests.post(os.environ['CIVICRM_URL'], data={
        'entity':'Job',
        'action':'execute',
        'api_key':os.environ['CIVICRM_API_KEY'],
        'key':os.environ['CIVICRM_SITE_KEY']}))

def main():
    """Makes a scheduler to run the CiviCRM jobs periodically."""
    signal.signal(signal.SIGTERM, sigterm_handler)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    scheduler = apscheduler.schedulers.blocking.BlockingScheduler()
    scheduler.add_job(civicrm_cron, 'interval', minutes=5)
    scheduler.start()

if __name__ == "__main__":
    main()
