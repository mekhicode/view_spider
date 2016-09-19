# encoding: utf-8
#!/usr/bin/env python
import sys
import json
import time

import datetime
import json
import redis
import pika

# LOGGING_HOST = "localhost"
# from camelia_spider.notify import send_mail

try:
    import spider.local_settings as settings
except Exception, e:
    import spider.settings


class Logging():
    """
    there is the logging to Redis to analysis log and collecting
    :param  level : {'0': "DEBUG",'1': "INFO",'2': "WARNING",'3': "ERROR",'4': "CRITICAL",}
            name : the project name
            message : the must be json format

    :returns None
    """

    def __init__(self):
        self.getFormatter = None

    def setFormatter(self, asctime, name, levelname, message):
        return "%s - %s - %s - %s" % (asctime, name, levelname, message)

    def getLevel(self, level):
        data = {
            '0': "DEBUG",
            '1': "INFO",
            '2': "WARNING",
            '3': "ERROR",
            '4': "CRITICAL",
        }
        return data.get(level, "INFO")

    def log(self, level, name, message):
        try:
            if isinstance(message, dict):
                pass
            else:
                message = json.loads(message)
            now = datetime.datetime.now()
            time_now = now.strftime('%Y-%m-%d %H:%M:%S')
            self.getFormatter = self.setFormatter(time_now, self.getLevel(str(level)), name, message)
            # tasks = list()
            # map(lambda x: tasks.append(gevent.spawn(self.save_to_mq)), xrange(1))
            # gevent.spawn(self.save_to_mq).join()
            # self.save_to_mq()
        except Exception, e:
            print e
            # def send_mail(title, info, exception, name, product_id, from_spider, sync):
            # temp_data = {}
            # temp_data['Exception'] = e
            # temp_data['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            # send_mail('Logging Error', temp_data)

    def save_to_mq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=settings.RABBIT_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='log_queue', durable=True)
        channel.basic_publish(exchange='',
                              routing_key='log_queue',
                              body=self.getFormatter,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        connection.close()

if __name__ == "__main__":
    for i in xrange(0, 10, 1):
        message = {"qwe": i+1000, "a": i + 100}
        stats = {"name": "admin", "password": "admin"}
        dictMerged1 = dict(message.items() + stats.items())
        cameliaLogging = Logging()
        cameliaLogging.log("1", "test", dictMerged1)