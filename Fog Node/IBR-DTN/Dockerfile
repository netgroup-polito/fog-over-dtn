FROM debian:8.2

RUN apt-get update && apt-get install -y \
      git vim-nox net-tools tmux g++ libpth-dev make dh-autoreconf ca-certificates libicu52 libpsl0 libssl1.0.0 openssl pkg-config \
      --no-install-recommends \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN  cd  \
  && git clone https://github.com/ibrdtn/ibrdtn.git \
  && cd ibrdtn/ibrcommon/ \
  && ./autogen.sh \
  && ./configure && make && make install \
  && cd ../ibrdtn/ \
  && ./autogen.sh \
  && ./configure && make && make install \
  && echo "include /usr/local/lib/*" >> /etc/ld.so.conf && ldconfig

COPY dtn-default.conf ./

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

CMD [ "dtnd", "-c", "dtn.conf" ]

ENTRYPOINT ["./entrypoint.sh"]
