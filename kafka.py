import atexit
import json
import logging
import random
import threading

from confluent_kafka import Producer

from settings import conf

logger = logging.getLogger(__name__)

producer = Producer(conf)


def _delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        logger.warning('Message delivery failed: {}'.format(err))
    else:
        logger.info('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def store_in_big_data(topic, bulk_data):
    for data in bulk_data:
        try:
            producer.produce(topic, json.dumps(data).encode('utf-8'), callback=_delivery_report)
            producer.poll(0)
        except BufferError:
            flush_queue()
            producer.produce(topic, json.dumps(data).encode('utf-8'), callback=_delivery_report)
            producer.poll(0)
        except:
            logger.warning("Unexpected error in storing in big data!")
            producer.poll(0)

    random_flush_chance = random.randint(1, 500)
    if random_flush_chance == 1:
        logger.info("Random chance for flush queue!")
        threading.Thread(target=flush_queue).start()


def flush_queue():
    logger.info("Flushing queue")
    producer.flush()


atexit.register(flush_queue)
