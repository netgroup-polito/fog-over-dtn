FROM debian:8.2
MAINTAINER Politecnico di Torino

RUN apt-get update && apt-get install -y \
      git g++ libpth-dev make dh-autoreconf ca-certificates libicu52 libpsl0 libssl1.0.0 openssl libsqlite3-dev pkg-config \
      python python-dev python-distribute python-pip \
      vim-nox net-tools telnet \
      --no-install-recommends \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN cd \
  && git clone https://github.com/ibrdtn/ibrdtn.git \
  && cd ibrdtn/ibrcommon/ \
  && ./autogen.sh \
  && ./configure && make && make install \
  && cd ../ibrdtn/ \
  && ./autogen.sh \
  && ./configure --with-sqlite && make && make install \
  && echo "include /usr/local/lib/*" >> /etc/ld.so.conf && ldconfig
