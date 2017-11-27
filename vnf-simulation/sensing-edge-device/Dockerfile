FROM base-dtn
MAINTAINER Politecnico di Torino

ADD requirements.txt ./
RUN pip install -r requirements.txt

ADD gateway-mqtt-dtn.py ./
ADD mqtt-publisher.py ./
ADD mqtt-direct-publisher.py ./
ADD dtn-default.conf ./

ADD start.sh start.sh
RUN chmod +x start.sh

ENTRYPOINT ["dtnd", "-c", "dtn-default.conf"]
