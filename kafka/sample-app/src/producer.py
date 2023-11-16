from threading import Thread
import asyncio

import confluent_kafka
from confluent_kafka import KafkaException
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from loguru import logger
from schema import TestSchema
from config import get_config
env = get_config()

if env.runtime_env == 'local':
    kafka_config = {
        'bootstrap.servers' : env.KAFKA_BOOTSTRAP_SERVERS,
        'security.protocol': env.KAFKA_SECURITY_PROTOCOL
    }
    sr_config = { 
        'url': env.KAFKA_SR_URL 
    }
else:
    kafka_config = {
        'bootstrap.servers' : env.KAFKA_BOOTSTRAP_SERVERS,
        'security.protocol': env.KAFKA_SECURITY_PROTOCOL,
        'sasl.mechanism': env.KAFKA_SASL_MECHANISM,
        'sasl.username': env.KAFKA_SASL_USERNAME,
        'sasl.password': env.KAFKA_SASL_PASSWORD
    }
    sr_config = { 
        'url': env.KAFKA_SR_URL, 
        'basic.auth.user.info' : env.KAFKA_SR_AUTH 
    }

class Producer:
    def __init__(self, configs, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)

    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value):
        """
        An awaitable produce method.
        """
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)
        self._producer.produce(topic, value, on_delivery=ack)
        return result

    def produce2(self, topic, value, on_delivery):
        """
        A produce method in which delivery notifications are made available
        via both the returned future and on_delivery callback (if specified).
        """
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(
                    result.set_result, msg)
            if on_delivery:
                self._loop.call_soon_threadsafe(
                    on_delivery, err, msg)
        self._producer.produce(topic, value, on_delivery=ack)
        return result
    
    def produce3(self, topic, key, value, on_delivery):
        result = self._loop.create_future()

        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(
                    result.set_result, msg)
            if on_delivery:
                self._loop.call_soon_threadsafe(
                    on_delivery, err, msg)
        self._producer.produce(topic=topic, key=key, value=value, on_delivery=ack)
        return result

class Worker:
    def __init__(self) -> None:
        self.aioproducer = Producer(kafka_config)
        self.topic = env.TEST_TOPIC
        self.schema_registry_client = SchemaRegistryClient(sr_config)

    async def process(self) -> None:
        while True:
            try:
                msg = TestSchema.fake()
                string_serializer = StringSerializer('utf_8')
                avro_serializer = AvroSerializer(
                    self.schema_registry_client, 
                    msg.avro_schema(), 
                    lambda obj, sc : msg.asdict()
                    )
                
                k = string_serializer(str(msg.id), ctx=None)
                v = avro_serializer(msg, SerializationContext(self.topic, MessageField.VALUE))
                
                await self.aioproducer.produce3(
                    topic=self.topic,
                    key=k, value=v, on_delivery=self.delivery_report)
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"worker unconsidered error : {e}")
                await asyncio.sleep(2)
    
    async def delivery_report(self, err, msg):
        if err is not None:
            logger.error(f"Delivery failed for User record {msg.key()}: {err}")
            return
    
    def close(self) -> None:
        logger.info("produce worker close...")
        if self.aioproducer:
            self.aioproducer.close()
        logger.info("produce worker closed")