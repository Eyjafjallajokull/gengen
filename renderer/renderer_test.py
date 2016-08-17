import pika
import redis
QUEUE = 'render'

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue=QUEUE)

r = redis.StrictRedis(host='redis', port=6379, db=0)

def process(ch, method, props, body):
    print(" [x] Received %r" % body)
    import time
    time.sleep(.1)
    r.set('rendered_'+body, 1)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(process, queue=QUEUE)

print(' [*] Waiting for messages.')
channel.start_consuming()
