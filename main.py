from classes.worker import Worker
from classes.logger import Logger
from classes.proxy_manager import ProxyManager
from datetime import datetime
import json


def main():
    lg = Logger()
    log = lg.log
    err = lg.err
    suc = lg.suc

    pm = ProxyManager()

    log('Reading config from config.json')
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
    except IOError:
        err('Unable to read config.json')
        return -1
    else:
        try:
            drop_time = datetime.strptime(config['drop_time'], '%x %X')
        except ValueError as e:
            err('Couldn\'t parse drop time from config file. Ensure format is MM/DD/YY HH:MM:SS (24 hour)')
            print(e)
            return -1
        else:
            suc('Loaded DUMMY: [{}], DROP TIME: [{}], RETRY DELAY: [{}s]'.format(
                config['dummy_variant'],
                config['drop_time'],
                config['retry_delay']
            ))
            # TODO: make sure all fields are filled

    log('Reading tasks from tasks.json')
    try:
        with open('tasks.json') as task_file:
            tasks = json.load(task_file)
    except IOError:
        err('Unable to read tasks.json')
        return -1
    else:
        suc('Read {} tasks from tasks.json'.format(len(tasks)))

    log('Reading proxies from proxies.txt')
    try:
        with open('proxies.txt') as proxy_file:
            proxies = proxy_file.readlines()
            pm.load_proxies(proxies)
    except IOError:
        err('Unable to read proxies.txt')
        return -1
    else:
        suc('Read {} proxies from proxies.txt'.format(len(proxies)))

    log('Loading tasks')
    workers = list()
    for index, task in enumerate(tasks['tasks']):
        if task['use_proxy']:
            proxy = pm.get_new_proxy()
        else:
            proxy = None
        w = Worker(
            worker_id=index,
            billing=task,
            dummy_variant=config['dummy_variant'],
            drop_time=drop_time,
            retry=float(config['retry_delay']),
            proxy=proxy
        )
        workers.append(w)
        workers[index].start()


if __name__ == '__main__':
    main()


# todo: add try/catch for valueerrors
# todo: figure out when session is dead and we need to restart
# todo: add account login
# todo: use most recent form build id not just 0 or 1

# 429 = cf rate limit = L
# 5XX = server is fucked, keep trying every few seconds
