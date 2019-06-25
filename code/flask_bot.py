#!/usr/bin/env python3
"""Example bot that returns a synchronous response."""

from flask import Flask, request, json
import requests
from httplib2 import Http
from json import dumps, loads
import logging
import ast
import os

jenkins_url_secret_file=os.environ['JENKINS_URL_SECRET_FILE']
with open(jenkins_url_secret_file, 'r') as jenkin_file:
    jenkins_job_url=jenkin_file.read().replace('\n', '')

gchat_webhook_secret_file=os.environ['GCHAT_WEBHOOK_SECRET_FILE']
with open(gchat_webhook_secret_file, 'r') as gchat_file:
    chat_webhook=gchat_file.read().replace('\n', '')

gchat_webhook_endpoint='/'+os.environ['GCHAT_WEBHOOK_ENDPOINT']
gchat_bot_endpoint='/'+os.environ['GCHAT_BOT_ENDPOINT']

def str2bool(bool_str):
  return bool_str.lower() in ("yes", "true", "t", "1")

app = Flask(__name__)

def contains_word(msg, req_directive):
    return (' ' + req_directive + ' ') in (' ' + msg + ' ')

@app.route(gchat_bot_endpoint, methods=['POST'])
def on_event():
  """Handles an event from Hangouts Chat."""
  event = request.get_json()
  if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
    text = 'Thanks for adding me to "%s"!' % event['space']['displayName']
  elif event['type'] == 'MESSAGE' :
    if contains_word( event['message']['argumentText'].lower(), 'deploy' ) : 
      msg_arg=event['message']['argumentText'].split(" ",3)
      payload={'tag':msg_arg[2]}
      response = requests.get(jenkins_job_url,json=payload) 
      text = response.text
    else :
      text = 'You said: `%s`' % event['message']['text']
  else:
    return
  return json.jsonify({'text': text})

@app.route(gchat_webhook_endpoint, methods=['POST', 'GET'])
def post_msg():

  #Receive the data in scan_result and remove the layers_details, which might overflow the length limit in Google API
  scan_result = loads(request.data)
  try: 
    del scan_result['contents']['scanSummary']['layer_details'] 
  except KeyError:
    pass
  app.logger.debug('Scan Result received is: %s', scan_result)
  bot_message = {'text':dumps(scan_result)}
  app.logger.debug('Bot message to be sent is: %s', bot_message)
  app.logger.debug('Message will be posted to this gChat Web Hook: %s',chat_webhook)
  #Call Google API
  message_headers = { 'Content-Type': 'application/json; charset=UTF-8'}
  http_obj = Http()
  response = http_obj.request(uri=chat_webhook,method='POST',headers=message_headers,body=dumps(bot_message),)
  app.logger.debug('Response from Google Chat Webhook: %s', response)
  #return make_response(json.jsonify({'status':'ok','text': scan_result}), 201)
  return 'OK'

if __name__ == '__main__':
  formatter = logging.Formatter( "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
  handler = logging.StreamHandler()
  handler.setLevel(logging.DEBUG)
  handler.setFormatter(formatter)
  app.logger.addHandler(handler)
  app.run(port=5000, host='0.0.0.0', debug=str2bool(os.environ['DEBUG']))
