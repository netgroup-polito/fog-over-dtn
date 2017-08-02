FROM python:2-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY filter_data.py ./

COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

CMD [ "python", "filter_data.py" ]

ENTRYPOINT ["./entrypoint.sh"]