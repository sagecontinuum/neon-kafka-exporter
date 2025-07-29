#!/usr/bin/env python3
import argparse
import logging
import time
from waggle.plugin import Plugin
from kafka import KafkaConsumer,TopicPartition
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import AvroMessageSerializer
import os
import sys
from datetime import datetime
from datetime import timezone
import pytz


def init_kafka():
    REGISTRY_URL = os.getenv('KAFKA_REGISTRY_URL')
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

def publish_values(plugin, topic_prefix, values, exclude_vars):
    values['readout_time'] = int(values['readout_time'].timestamp()*10**9)
    for key in list(values.keys()):
        if key not in exclude_vars:
            if isinstance(values[key], (int, float, str)):
                #safeguard for pywaggle publishing (same as their own check)
                plugin.publish(f"neon.{topic_prefix}.{str(key).lower()}", values[key], timestamp=values['readout_time'])
    return

def send_data_from_topic(consumer, topic, delay, exclude_vars, startTime, endTime=None):
    tp = TopicPartition(topic, 0)
    assigned_topic = [tp]
    consumer.assign(assigned_topic)
    rec_in  = consumer.offsets_for_times({tp:startTime.timestamp() * 1000})
    if endTime is not None:
        rec_out = consumer.offsets_for_times({tp:endTime.timestamp() * 1000})
    else:
        rec_out = None

    if rec_in[tp] is None:
        logging.info('topic: %s has no messages to stream',topic)
        return
    consumer.seek(tp, rec_in[tp].offset)
    with Plugin() as plugin:
        logging.info('Streaming data for topic: %s, startTime: %s - endTime: %s, delay: %s',topic, startTime,endTime, delay)
        count_msgs = 0
        last_publish_time = 0
        try:
            for msg in consumer:
                if rec_out is not None and msg.offset > rec_out[tp].offset:
                    break
                now = time.time()
                if delay > 0:
                    if now - last_publish_time >= delay:
                        publish_values(plugin, topic, msg.value, exclude_vars)
                        count_msgs += 1
                        last_publish_time = now
                else:
                    publish_values(plugin, topic, msg.value)
                    count_msgs += 1
        finally:
            logging.info('Done streaming data for topic: %s, wrote %s records',topic,str(count_msgs))
    return

def subscribe_topic_stream(consumer, topics, delay, exclude_vars):
    consumer.subscribe(topics=topics)
    with Plugin() as plugin:
        logging.info('Subscribe to topic: %s, delay: %s',topics, delay)
        count_msgs = 0
        last_publish_time = {topic: 0 for topic in topics}
        try:
            for msg in consumer:
                current_topic = msg.topic
                if current_topic not in topics:
                    logging.warning(f"Received message for unexpected topic '{current_topic}'. Skipping publish.")
                    continue
                now = time.time()
                if delay > 0:
                    if now - last_publish_time[current_topic] >= delay:
                        publish_values(plugin, current_topic, msg.value, exclude_vars)
                        count_msgs += 1
                        last_publish_time[current_topic] = now
                else:
                    publish_values(plugin, current_topic, msg.value)
                    count_msgs += 1
        finally:
            logging.info('Done streaming data for topics: %s, wrote %s records',topics,str(count_msgs))
    return

def convert_input_time_to_datetime(time_input,time_type):
    try:
        time_format = datetime.fromisoformat(time_input)
    except:
        logging.critical('Invalid time: ' + str(time_input) + ' for ' +str(time_type))
        sys.exit()
    return time_format

def mod_tz(time):
    utc_tz = pytz.UTC
    if time is None:
        time_tz = time
    elif time.tzinfo is None or time.tzinfo != timezone.utc:
        time_tz = utc_tz.localize(time)
    else:
        time_tz = time
    return time_tz

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",choices=['fixed-time','subscribe'],help="Mode to run plugin. Options: fixed-time,subscribe")
    parser.add_argument("--topics",nargs="+",help="Kafka topic to stream data from")
    parser.add_argument("--startTime", help="Start time in isoformat")
    parser.add_argument("--endTime",help="End time in isoformat")
    parser.add_argument("--delay", type=int, default=60, help="Delay in seconds between data publishes")
    parser.add_argument("--excludeVars",nargs="+",default=['readout_time','site_id'],help="Exclude variables in a sensor topic")

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
    topics = args.topics
    delay = args.delay
    exclude_vars = args.excludeVars

    start_time_input = args.startTime
    end_time_input = args.endTime
    if start_time_input is not None:
        startTime = convert_input_time_to_datetime(start_time_input,'--startTime')
    else:
        startTime = None

    if end_time_input is not None:
        endTime = convert_input_time_to_datetime(end_time_input,'--endTime')
    else:
        endTime = None

    # check that UTC is provided as a timezone
    startTime = mod_tz(startTime)
    endTime = mod_tz(endTime)

    mode = args.mode
    if mode == 'fixed-time':
        # if mode == fixed-time, startTime and endTime have to be provided. Optional for topic
        if startTime is not None and endTime is not None:
            if endTime <= startTime:
                logging.critical('endTime is before startTime - no data available.')
                sys.exit()
            if topics is None:
                topics = sensor_topics

            for iTopic in topics:
                if not iTopic in sensor_topics:
                    logging.critical('Topic: ' + str(iTopic) + ' not available or not supported.')
                    continue
                send_data_from_topic(consumer, iTopic, delay, exclude_vars, startTime, endTime)
        else:
            logging.critical('Not supporting this configuration for %s',mode)
            sys.exit()
    elif mode == 'subscribe':
        #if mode == subscribe, topics optional, defaults to all sensor_topics, startTime and endTime should not be provided
        if startTime is None and endTime is None:
            if topics is None:
                topics = sensor_topics

            final_topics = []
            for iTopic in topics:
                if not iTopic in sensor_topics:
                    logging.critical('Topic: ' + str(iTopic) + ' not available or not supported.')
                else:
                    final_topics.append(iTopic)
            subscribe_topic_stream(consumer, final_topics, delay, exclude_vars)
        else:
            logging.critical('Not supporting this configuration for %s',mode)
            sys.exit()
    else:
        logging.critical('Not supporting this mode: %s',mode)
        sys.exit()

if __name__ == "__main__":
    main()
