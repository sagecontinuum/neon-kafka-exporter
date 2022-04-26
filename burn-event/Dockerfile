#docker build -t sagecontinuum/neon-kafka .
#docker run -it --rm sagecontinuum/neon-kafka bash
FROM python:3.9

RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
        htop \
        unzip \
        vim \
        zip \
        kafkacat \
        && \
        rm -rf /var/lib/apt/lists/*

WORKDIR /neon/
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY neon.py neon.py