# Neon Kafka Exporter

This is a plugin to export Neon's Kafka data stream to SDR.

## Overview

Plugins contain both code and packaging information. In this example, we've organized them as follows:

1. The code consists of:
    * [main.py](./main.py). Main plugin code.
    * [requirements.txt](./requirements.txt). Python dependencies file. Add any required modules to this file.

2. The packaging information consists of:
    * [sage.yaml](./sage.yaml). Defines plugin info used by [ECR](https://portal.sagecontinuum.org). You must update this for your example.
    * [Dockerfile](./Dockerfile). Defines plugin code and dependency bundle. You can update this if you have additional dependencies not covered by [requirements.txt](./requirements.txt).
    * [ecr-meta](./ecr-meta/). Science metadata for ECR.

## Create .env file with Kafka credentials
Create an .env file with Kafka credentials. Note that `.gitignore` excludes the .env files.

.env format:
```
KAFKA_BROKER=
KAFKA_USERNAME=
KAFKA_PASSWORD=
```

## Neon Kafka Data Stream Topics
Available topics from the Kafka stream with description to some topics or see this image for more information about the sensors [link](https://www.neonscience.org/sites/default/files/styles/max_2600x2600/public/2021-04/2021_04_MDP-Measurements-Table-2021-Master.png?itok=UdCXLRmT):
- 'reading.sensor.prt', - Singal aspirated air temperature
- 'reading.sensor.mti300ahrs', - 3D wind attitude and motion reference
- 'reading.sensor.li191r', - Photosynthetically active radiation (quantum line)
- 'event.rtu.pump',
- 'reading.phenocam.rgbimage', - Phenology images [RGB]
- 'reading.sensor.hfp01sc', - Soil heat flux plate
- 'reading.sensor.mcseries',
- 'reading.sensor.picarro3way',
- 'reading.sensor.hmp155', - Relative humidity
- 'event.cnc.ecte',
- 'reading.sensor.t7610', - Precipitation
- 'reading.sensor.csat3', - 3D wind speed, direction and sonic temperature
- 'reading.sensor.pqs1', - Photosynthetically active radiation (PAR)
- 'reading.sensor.mwseries',
- 'event.rtu.grape',
- 'reading.sensor.g2131i_raw', - Atmospheric CO2 isotopes
- 'event.cnc.ecse',
- 'event.rtu.events',
- 'reading.sensor.nr01', - Shortwave and longwave radiation (net radiometer)
- 'reading.sensor.grape',
- 'reading.sensor.windobserverii', - 2D wind speed and direction
- 'reading.sensor.pressuretransducer',
- 'reading.sensor.li840a', - CO2 concentration storage
- 'event.cnc.pumps',
- 'reading.sensor.si111', - IR biological temperature
- 'reading.sensor.ptb330a', - Barometric pressure
- 'reading.sensor.li7200_raw', - CO2 and H2O concentrations turbulent
- 'reading.sensor.pump',
- 'reading.sensor.dualfan',
- 'reading.sensor.l2130i_raw', - Atmospheric H2O isotopes
- 'reading.phenocam.irimage', - Phenology images (IR)

Files provided for the burn event:
- 'reading.sensor.li191r', - Photosynthetically active radiation (quantum line)
- 'reading.sensor.pqs1', - Photosynthetically active radiation (PAR)
- 'reading.sensor.mti300ahrs', - 3D wind attitude and motion reference
- 'reading.sensor.ptb330a', - Barometric pressure
- 'reading.sensor.li7200_raw', - CO2 and H2O concentrations turbulent
- 'reading.sensor.hfp01sc', - Soil heat flux plate
- 'reading.sensor.li840a', - CO2 concentration storage
- 'reading.sensor.t7610', - Precipitation
- 'reading.sensor.g2131i_raw', - Atmospheric CO2 isotopes
- 'reading.sensor.prt', - Singal aspirated air temperature
- 'reading.sensor.windobserverii', - 2D wind speed and direction
- 'reading.sensor.hmp155', - Relative humidity
- 'reading.sensor.pressuretransducer',
- 'reading.sensor.si111', - IR biological temperature
- 'reading.sensor.l2130i_raw', - Atmospheric H2O isotopes
- 'reading.sensor.csat3', - 3D wind speed, direction and sonic temperature
- 'reading.sensor.nr01', - Shortwave and longwave radiation (net radiometer)

For each file, refer to the Algorithm Theoretical Basis Document ATBD for each variable on [NEONs Data portal](https://data.neonscience.org/data-products/explore) to convert the raw data to useable data. For example, `reading.sensor.windobserverii` corresponds to [2D Wind Speed and direction](https://data.neonscience.org/data-products/DP1.00001.001/RELEASE-2021) with the following [ATBD document](https://data.neonscience.org/api/v0/documents/NEON.DOC.000780vB)

For more information about the NEON Nodes see [link](https://www.neonscience.org/resources/research-support/mobile-deployment-platforms)

## Neon Kafka Data Exporter - plugin

### Plugin usage
Two modes are currently supported for the plugin:
- subscribe: plugin is subscribing to a topic or multiple topics
- fixed-time: plugin is streaming data either for all the topics or a provided topic with start and end datetime.

Full argument list:
```
--mode subscribe or fixed-time
--topics topic from the above list
--startTime start time in isoformat with timezone UTC
--endTIme end time in isoformat with timezone UTC
```
Example for `--startTime` and `--endTime`:
```
2022-05-04T05:00:00+00:00
2022-05-04T05:00
2022-05-04
```
If the user does not provide a timezone aware `--startTime` or `--endTime`, it will default to UTC. If either one is not in UTC timezone it will be modify to UTC.

Or generate one with this command with desired time:
```
import datetime
print(datetime.datetime(2022,4,18,5,0,tzinfo=datetime.timezone.utc).isoformat())
```

For `--mode subscribe`, the user can pass in the following command line arguments:
```
--mode subscribe 
--topics reading.sensor.mti300ahrs reading.sensor.prt
```
`--topics` can be a list of topics or just one topic.

Full usage (reference Docker section for building):
```
docker run --env-file=.env -it --rm sagecontinuum/plugin-neon-kafka-exporter --mode subscribe --topics reading.sensor.mti300ahrs reading.sensor.prt
```
Example output:
```
Updating subscribed topics to: ['reading.sensor.mti300ahrs', 'reading.sensor.prt']
Subscribe to topic: ['reading.sensor.mti300ahrs', 'reading.sensor.prt']
...
Updated partition assignment: [TopicPartition(topic='reading.sensor.mti300ahrs', partition=0), TopicPartition(topic='reading.sensor.prt', partition=0)]
Done streaming data for topics: ['reading.sensor.mti300ahrs', 'reading.sensor.prt'], wrote 2805 records
```

The user can also subscribe to all the `sensor topics` by not providing any topics:
```
--mode subscribe
```

Full usage (reference Docker section for building):
```
docker run --env-file=.env -it --rm sagecontinuum/plugin-neon-kafka-exporter --mode subscribe
```

For `--mode fixed-time`, the user can pass in the following command line arguments:
```
--mode fixed-time
--startTime 2022-05-04T05:00:00+00:00
--endTime 2022-05-04T06:00:00+00:00
```
This will stream all the sensor topics from `--startTime` to `--endTime`.

Full usage:
```
docker run --env-file=.env -it --rm sagecontinuum/plugin-neon-kafka-exporter --mode fixed-time --startTime 2022-05-04T05:00:00+00:00 --endTime 2022-05-04T06:00:00+00:00
```
Possible output:
```
Streaming data for topic: reading.sensor.windobserverii, startTime: 2022-05-04 05:00:00+00:00 - endTime: 2022-05-04 06:00:00+00:00
Done streaming data for topic: reading.sensor.windobserverii, wrote 3601 records
Streaming data for topic: reading.sensor.pressuretransducer, startTime: 2022-05-04 05:00:00+00:00 - endTime: 2022-05-04 06:00:00+00:00
....
```
For one topic:
```
docker run --env-file=.env -it --rm sagecontinuum/plugin-neon-kafka-exporter --mode fixed-time --topics reading.sensor.mti300ahrs --startTime 2022-05-04T05:00:00+00:00 --endTime 2022-05-04T06:00:00+00:00
```

### Docker
Docker build:
```
docker build -t sagecontinuum/plugin-neon-kafka-exporter .
```
Docker run:
```
docker run --env-file=.env -it --rm sagecontinuum/plugin-neon-kafka-exporter --mode subscribe --topics reading.sensor.mti300ahrs
```
### Kubernetes
Create secrets from .env:
```
kubectl create secret generic neon-env --from-env-file=.env
```
Deploy app:
```
kubectl create -f deployment.yaml
```

## Neon Kafka Data exporter for the burn event
Neon and Sage collected data for a controlled fire. In the directory [burn-event](burn-event) contains the scripts to get the streaming data into a pickle file. Note that the scripts must be ran on the WSN node and have access to the Kafka and schema registry endpoint.

Usage of the script:
Build:
```
docker build -t sagecontinuum/neon-kafka-exporter .
```
Run:
```
docker run -v $(pwd):/neon  --env-file=.env -it --rm sagecontinuum/neon-kafka-exporter python3 neon.py
```
Output:
```
Retreiving Schema
Connecting to Kafka
All topics from stream:
{'reading.sensor.pressuretransducer', 'reading.sensor.mwseries', 'reading.sensor.l2130i_raw', 'reading.sensor.pqs1', 'reading.sensor.li840a', 'reading.phenocam.rgbimage', 'reading.sensor.csat3', 'reading.sensor.li191r', 'reading.sensor.mti300ahrs', 'reading.sensor.pump', 'reading.sensor.mcseries', 'reading.sensor.li7200_raw', 'reading.sensor.t7610', 'event.rtu.pump', 'event.cnc.pumps', 'reading.sensor.si111', 'event.rtu.grape', 'reading.sensor.g2131i_raw', 'event.cnc.ecte', 'event.rtu.events', 'reading.sensor.windobserverii', 'reading.sensor.nr01', 'reading.phenocam.irimage', 'reading.sensor.ptb330a', 'event.cnc.soil', 'reading.sensor.grape', 'reading.sensor.prt', 'event.cnc.ecse', 'reading.sensor.hfp01sc', 'reading.sensor.dualfan', 'reading.sensor.hmp155', 'reading.sensor.picarro3way'}

Desired sensor topics
['reading.sensor.pressuretransducer', 'reading.sensor.l2130i_raw', 'reading.sensor.pqs1', 'reading.sensor.li840a', 'reading.sensor.csat3', 'reading.sensor.li191r', 'reading.sensor.mti300ahrs', 'reading.sensor.li7200_raw', 'reading.sensor.t7610', 'reading.sensor.si111', 'reading.sensor.g2131i_raw', 'reading.sensor.windobserverii', 'reading.sensor.nr01', 'reading.sensor.ptb330a', 'reading.sensor.prt', 'reading.sensor.hfp01sc', 'reading.sensor.hmp155']

Date Range: 2022-04-15 12:00:00+00:00 - 2022-04-18 05:00:00+00:00
i: 0, total: 17, Topic: reading.sensor.pressuretransducer
Wrote 6785981 messages

i: 1, total: 17, Topic: reading.sensor.l2130i_raw
Wrote 158696 messages

i: 2, total: 17, Topic: reading.sensor.pqs1
Wrote 701902 messages

i: 3, total: 17, Topic: reading.sensor.li840a
Wrote 138807 messages

i: 4, total: 17, Topic: reading.sensor.csat3
Wrote 4680001 messages

i: 5, total: 17, Topic: reading.sensor.li191r
Wrote 144184 messages

i: 6, total: 17, Topic: reading.sensor.mti300ahrs
Wrote 9336403 messages

i: 7, total: 17, Topic: reading.sensor.li7200_raw
Wrote 4679516 messages

i: 8, total: 17, Topic: reading.sensor.t7610
Wrote 234001 messages

i: 9, total: 17, Topic: reading.sensor.si111
Wrote 233901 messages

i: 10, total: 17, Topic: reading.sensor.g2131i_raw
Wrote 151870 messages

i: 11, total: 17, Topic: reading.sensor.windobserverii
Wrote 143369 messages

i: 12, total: 17, Topic: reading.sensor.nr01
Wrote 234001 messages

i: 13, total: 17, Topic: reading.sensor.ptb330a
Wrote 23406 messages

i: 14, total: 17, Topic: reading.sensor.prt
Wrote 467984 messages

i: 15, total: 17, Topic: reading.sensor.hfp01sc
Wrote 14419 messages

i: 16, total: 17, Topic: reading.sensor.hmp155
Wrote 467975 messages
```
Files sizes:
```
1.2G: reading.sensor.csat3.pkl
 59M: reading.sensor.g2131i_raw.pkl
2.4M: reading.sensor.hfp01sc.pkl
 86M: reading.sensor.hmp155.pkl
 46M: reading.sensor.l2130i_raw.pkl
 17M: reading.sensor.li191r.pkl
4.2G: reading.sensor.li7200_raw.pkl
 30M: reading.sensor.li840a.pkl
3.8G: reading.sensor.mti300ahrs.pkl
 65M: reading.sensor.nr01.pkl
 81M: reading.sensor.pqs1.pkl
797M: reading.sensor.pressuretransducer.pkl
 56M: reading.sensor.prt.pkl
3.9M: reading.sensor.ptb330a.pkl
 33M: reading.sensor.si111.pkl
 51M: reading.sensor.t7610.pkl
 31M: reading.sensor.windobserverii.pkl
```
## Exploratory Data Analysis of the data:
After generating all the files for the burn event, the user can utilize the notebook [exploratory-data-analysis.ipynb](burn-event/exploratory-data-analysis.ipynb) to start using the data.