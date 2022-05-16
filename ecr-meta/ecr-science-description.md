# Neon Kafka Exporter
In collaboration between Sage and Neon, a [Mobile Deployment Platform](https://www.neonscience.org/resources/research-support/mobile-deployment-platforms) can now stream data to the Sage Data Repository via the Wild Sage Node in real-time with this Edge Application (referred to as a plugin).
## Neon Kafka Data Stream Topics
Available topics from the Kafka stream with description to some topics:
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

![NEON Sensors](https://www.neonscience.org/sites/default/files/styles/max_2600x2600/public/2021-04/2021_04_MDP-Measurements-Table-2021-Master.png?itok=UdCXLRmT)

For each file, refer to the Algorithm Theoretical Basis Document ATBD for each variable on [NEONs Data portal](https://data.neonscience.org/data-products/explore) to convert the raw data to useable data. For example, `reading.sensor.windobserverii` corresponds to [2D Wind Speed and direction](https://data.neonscience.org/data-products/DP1.00001.001/RELEASE-2021) with the following [ATBD document](https://data.neonscience.org/api/v0/documents/NEON.DOC.000780vB)

For more information about the NEON Nodes see [link](https://www.neonscience.org/resources/research-support/mobile-deployment-platforms)

## Plugin usage
Reference Github REAME for usage in this [link](https://github.com/sagecontinuum/neon-kafka-exporter#readme)