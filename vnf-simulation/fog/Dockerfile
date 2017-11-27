FROM base-dtn
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y iptables \
      --no-install-recommends \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD gateway-dtn-mqtt.py ./
ADD dtn-default.conf ./

ADD start.sh start.sh
RUN chmod +x start.sh

ENTRYPOINT ["dtnd", "-c", "dtn-default.conf"]
