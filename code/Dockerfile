FROM ubuntu:16.04


ENV JENKINS_URL_SECRET_FILE ''
ENV GCHAT_WEBHOOK_SECRET_FILE ''
ENV GCHAT_WEBHOOK_ENDPOINT 'web-hook'
ENV GCHAT_BOT_ENDPOINT 'chat-bot'
ENV DEBUG False

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev && \
    pip install --upgrade pip

RUN pip install -r requirements.txt 

COPY ./flask_bot.py /app/flask_bot.py
EXPOSE 5000
ENTRYPOINT [ "python" ]
CMD [ "flask_bot.py" ]

