FROM biansepang/weebproject:buster

RUN git clone -b memew https://github.com/tofikdn/Man-Userbot /home/man-userbot/ \
    && chmod 777 /home/man-userbot \
    && mkdir /home/man-userbot/bin/

COPY ./sample_config.env ./config.env* /home/man-userbot/

WORKDIR /home/man-userbot/

RUN pip3 install -r https://raw.githubusercontent.com/tofikdn/Man-Userbot/memew/requirements.txt

CMD ["python3", "-m", "userbot"]
