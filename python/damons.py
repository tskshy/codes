# -*- coding: utf-8 -*-
import time
import subprocess
import logging

from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='damons.log',
                    filemode='a')


LIST = [
    {
        "keyword": "ThriftServer",
        "query_cmd": "jps|grep ThriftServer",
        "run_cmd": "sh /usr/servers/alihbase-1.1.1/bin/hbase-deamon.sh start thrift",
        "show_msg": "thrift server"
    }
]

scheduler = BlockingScheduler()


@scheduler.scheduled_job("cron", id="test_id", second=1)
def scheduler_test_func():
    for item in LIST:
        keyword = item.get("keyword")
        query_cmd = item.get("query_cmd")
        run_cmd = item.get("run_cmd")
        show_msg = item.get("show_msg")

        p = subprocess.Popen(query_cmd, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = p.communicate()
        str = stdout.decode()
        if keyword in str:
            logging.info("{0}, exists".format(show_msg))
        else:
            logging.info("{0}, not exists, run now".format(show_msg))
            subprocess.call(run_cmd, shell=True)


if __name__ == "__main__":
    #scheduler = BackgroundScheduler()
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    scheduler.configure(executors=executors, job_defaults=job_defaults)

    job = scheduler.add_job(scheduler_test_func)
    scheduler.start()
