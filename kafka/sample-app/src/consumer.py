import asyncio
from datetime import datetime
import sys

from confluent_kafka import Consumer
from confluent_kafka import KafkaException
from confluent_kafka.serialization import SerializationContext, MessageField, StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from loguru import logger
from schema import TestSchema
from config import get_config
env = get_config()

try:
    logger.remove(0)
except Exception:
    pass

logger.add(sys.stderr, format="{message}")

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


def dict_to_test(obj, ctx):
    """
    Converts object literal(dict) to a User instance.

    Args:
        obj (dict): Object literal(dict)

        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.
    """

    if obj is None:
        return None

    return TestSchema(id=obj['id'],
                value=obj['value'],
                timestamp=obj['timestamp'])    


class Worker:
    def __init__(self) -> None:
        self.topic = env.TEST_TOPIC
        self.schema_registry_client = SchemaRegistryClient(sr_config)
                
        schema = TestSchema.fake()
        self.string_deserializer = StringDeserializer('utf-8')
        self.avro_deserializer = AvroDeserializer(
                                self.schema_registry_client,
                                schema.avro_schema(),
                                dict_to_test)
        
        consumer_conf = kafka_config
        consumer_conf['group.id'] = "unique_id"
        consumer_conf['enable.auto.commit'] = "true"
        consumer_conf['auto.offset.reset'] = "latest" # earliest
        self.consumer = Consumer(consumer_conf)
        self.consumer.subscribe([self.topic])

    async def process(self) -> None:

        while True:
            try:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    raise KafkaException(msg.error())
                
                test_key : str = self.string_deserializer(msg.key()) #type:ignore
                test_data : TestSchema = self.avro_deserializer(
                    msg.value(), 
                    SerializationContext(msg.topic(), MessageField.VALUE)
                    ) #type:ignore

                if test_data is not None:
                    logger.info(f"msg info : {msg.key()}, {msg.topic()}, {msg.partition()}, {msg.offset()}")
                    # logger.info(f'test_key : {msg.key()}')
                    # logger.info(f'test_data : {test_data}')
                    ts : datetime = test_data.timestamp
                    logger.info(f"record {test_key} : \n"
                        + f"\tid: {test_data.id}\n"
                        + f"\tvalue: {test_data.value}\n"
                        + f"\ttimestamp: {ts.timestamp()}\n"
                        + f"\tdatetime: {ts.isoformat()}\n")

            except Exception as e:
                logger.error(f"worker unconsidered error : {e}")
                await asyncio.sleep(2)
    
    def close(self) -> None:
        logger.info("comsume worker close...")
        
        self.consumer.close()
        logger.info("comsume worker closed")