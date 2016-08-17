import pika
import uuid


class Queue(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()

    def register(self, queue):
        self.channel.queue_declare(queue=queue)

    def send(self, queue, msg):
        self.channel.basic_publish(exchange='',
                                   routing_key=queue,
                                   body=msg,
                                   mandatory=True)

    def close(self, ):
        self.connection.close()



