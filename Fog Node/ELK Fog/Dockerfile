FROM sebp/elk

# overwrite existing file
ADD /my-02-beats-input.conf /etc/logstash/conf.d/02-beats-input.conf

# overwrite existing file
ADD /my-30-output.conf /etc/logstash/conf.d/30-output.conf

# add new file
ADD /new-12-rpi-filter.conf /etc/logstash/conf.d/12-rpi-filter.conf

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD [ "/usr/local/bin/start.sh" ]
ENTRYPOINT ["/entrypoint.sh"]