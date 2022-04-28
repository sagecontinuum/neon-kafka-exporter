#!/usr/bin/env python3
import argparse
import logging
import time
import numpy as np
from waggle.plugin import Plugin
from kafka import KafkaConsumer,TopicPartition
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import AvroMessageSerializer
import os
import sys
from datetime import datetime
import json
import pytz


def init_kafka():
    REGISTRY_URL = "https://schemaregistry.mdp5.eng.neoninternal.org/apis/ccompat/v6"
    KAFKA_BROKER = os.getenv('KAFKA_BROKER')
    KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
    KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

    client = SchemaRegistryClient(REGISTRY_URL)
    avro_message_serializer = AvroMessageSerializer(client)

    consumer = KafkaConsumer(
        client_id="waggle",
        bootstrap_servers=[KAFKA_BROKER],
        api_version=(2,5,0),
        security_protocol='SASL_PLAINTEXT',
        sasl_mechanism='SCRAM-SHA-512',
        sasl_plain_username=KAFKA_USERNAME,
        sasl_plain_password=KAFKA_PASSWORD,
        auto_offset_reset='latest',
        key_deserializer=lambda key: key.decode(), # UTF decode the bytes into a string
        value_deserializer=avro_message_serializer.decode_message # Use the schema registry to deserialize the avro message
    )
    return consumer

def get_sensor_topics(topics):
    exclude_sensors = [
                        'reading.sensor.pump',
                        'reading.sensor.dualfan',
                        'reading.sensor.grape',
                        'reading.sensor.mwseries',
                        'reading.sensor.mcseries',
                        'reading.sensor.picarro3way',
                    ]

    sensor_topics = [
                        topic for topic in topics \
                        if topic.startswith('reading.sensor') and \
                            topic not in exclude_sensors
                    ]
    return sensor_topics

def send_data_from_topic(consumer,topic,date_start):
    tp = TopicPartition(topic, 0)
    assigned_topic = [tp]
    consumer.assign(assigned_topic)
    rec_in  = consumer.offsets_for_times({tp:date_start.timestamp() * 1000})
    if rec_in[tp] is None:
        logging.info('topic: %s has no messages to stream',topic)
        return
    consumer.seek(tp, rec_in[tp].offset)
    with Plugin() as plugin:
        logging.info('streaming data for topic: %s',topic)
        for msg in consumer:
            values = msg.value
            values['readout_time'] = values['readout_time'].isoformat()
            for key in list(values.keys()):
                if isinstance(values[key],bytes):
                    del values[key]
            plugin.publish("neon." + topic, values)
    logging.info('Done streaming data for topic: %s',topic)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="kafka topic to stream data from")
    args = parser.parse_args()
    logging.basicConfig(
                        level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S',
                    )
    logging.info("starting plugin.")
    consumer = init_kafka()
    all_topics = consumer.topics()
    sensor_topics = get_sensor_topics(all_topics)
    topic = args.topic
    if not topic in sensor_topics:
        sys.exit('Topic: ' + str(topic) + 'not available or not supported.')

    date_start = datetime.now(pytz.utc)

    print('topic: ' + str(topic))
    send_data_from_topic(consumer,topic,date_start)


if __name__ == "__main__":
    main()
