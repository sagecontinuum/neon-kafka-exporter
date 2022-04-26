#!/usr/bin/env python3
from kafka import KafkaConsumer,TopicPartition
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import AvroMessageSerializer
import sys
import datetime
import json
import pickle
import os

def write_data_to_json(consumer,date_in,date_out,topic,file):
    tp = TopicPartition(topic, 0)
    assigned_topic = [tp]
    consumer.assign(assigned_topic)
    rec_in  = consumer.offsets_for_times({tp:date_in.timestamp() * 1000})
    rec_out = consumer.offsets_for_times({tp:date_out.timestamp() * 1000})

    consumer.seek(tp, rec_in[tp].offset)
    count = 0
    with open(file, 'wb') as f:
        for msg in consumer:
            if msg.offset > rec_out[tp].offset:
                break
            values = msg.value
            values['readout_time'] = values['readout_time'].isoformat()
            pickle.dump(values, f)
            count += 1
    print("Wrote {c} messages".format(c=count))

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

REGISTRY_URL = "https://schemaregistry.mdp5.eng.neoninternal.org/apis/ccompat/v6"
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
KAFKA_USERNAME = os.getenv('KAFKA_USERNAME')
KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD')

print("Retreiving Schema")
client = SchemaRegistryClient(REGISTRY_URL)
avro_message_serializer = AvroMessageSerializer(client)

print("Connecting to Kafka")
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

all_topics = consumer.topics()

print('All topics from the stream:')
print(all_topics)
print('')

sensor_topics = get_sensor_topics(all_topics)
total_sensor_topics = str(len(sensor_topics))
print('Desired sensor topics')
print(sensor_topics)
print('')

date_in  = datetime.datetime(2022,4,15,12,0,tzinfo=datetime.timezone.utc)
date_out = datetime.datetime(2022,4,18,5,0,tzinfo=datetime.timezone.utc)

print("Date Range: {} - {}".format(str(date_in),str(date_out)))
for i,topic in enumerate(sensor_topics):
    file = topic+'.pkl'
    print('i: {}, total: {}, Topic: {}'.format(i,str(total_sensor_topics),topic))
    write_data_to_json(consumer,date_in,date_out,topic,file)
    print()