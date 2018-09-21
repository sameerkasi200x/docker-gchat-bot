## Integrating Docker Trusted Registry with Google Chat

Google Recently launched Google Chat for GSuite users. Though it is far from perfect, I found it quite useful and hope that it would become a good alternative to Slack. It allows you to have DM (one-on-one) chat and create rooms (kind of group chat) - generalized as a [*SPACE*](https://developers.google.com/hangouts/chat/concepts/cards). You can add [Chat Bots](https://developers.google.com/hangouts/chat/concepts/bots) to these spaces to automate tasks like voting, create calendar invite, setup video call etc. You can also setup [Incoming Webhooks](https://developers.google.com/hangouts/chat/how-tos/webhooks) in spaces so that you can deliver messages to spaces by remotely invoking a URL.

This is a simple Python code to implement team integration/communication for Docker Trusted Registry with Google Chat Bot and Google Chat's Incoming Webhook. In its current form it can be useful to:

1. Send notifications in a Google Chat Room whenever a new image is pushed to Docker Trusted Registry. This uses [DTR's webhook features](https://docs.docker.com/ee/dtr/user/create-and-manage-webhooks/).
2. Deploy latest image using [Jenkins's Generic Webhook Trigger](https://wiki.jenkins.io/display/JENKINS/Generic+Webhook+Trigger+Plugin). This particular implementation just triggers a Jenkins build which internally knows how to get the latest image (by using the GIT_COMMIT). But it is quite easy to pass the image tag as the body of the JSON message passed by Chat Bot to Jenkins's webhook endoint.

The code is based on two examples provided by Google:
+ [Simple Chat Bot with Python & Flask](https://developers.google.com/hangouts/chat/how-tos/bots-develop)
+ [Incoming webhook with Python](https://developers.google.com/hangouts/chat/quickstart/incoming-bot-python)

## Setting up dependencies

This code depends on setup of DTR, GitHub and Jenkins. Before you can starting using this code, you should also enable Google Chat API and register a service account.

1. Docker Trusted Registry (DTR) setup *(WIP - a different Markdown file to be added for this)*
2. GitHub Repository Setup *(WIP - a different Markdown file to be added for this)*
3. Jenkins Setup *(WIP - a different Markdown file to be added for this)*
4. Google Chat Account Setup *(WIP - a different Markdown file to be added for this)*

## Setting up this code as a Docker Swarm Service

This sample deploys the sample code as a service on [Docker Universal Control Plane](https://docs.docker.com/ee/ucp/) using Swarm orchestration. You might want to read a bit about Docker Swarm Service and [Layer-7 Routing using Interlock](https://docs.docker.com/ee/ucp/interlock/architecture/#routing-lifecycle) in Docker UCP. 

It is quite simple to enable [Layer-7 Routing in UCP](https://docs.docker.com/ee/ucp/interlock/deploy/) and you can refer to my GitHub repository [docker-ci-cd](https://github.com/sameerkasi200x/docker-ci-cd) for an example of how swarm service can be deployed with Layer-7 Routing.

Sample code to deploy this service

```
export old_tag=b1
export tag=$(date +%Y%m%d%H%M%S)

sed -i "s/${old_tag}/${tag}/g" google-chat-compose.yml
docker build -t dtr.example.com/myuser/google-chat-bot:$tag .
docker push dtr.example.com/myuser/google-chat-bot:$tag

docker stack deploy --compose-file google-chat-compose.yml google-chat
sleep 20
docker service logs -f google-chat_google-chat-bot

```

### Variables in Docker File/Docker Image
+ **JENKINS_URL_SECRET_FILE** - This is the path to the secret file where the URL for the Jenkins API url is stored. It is ideal to pass Jenkins Webhook URL using [Docker Swarm Secrets](https://docs.docker.com/engine/swarm/secrets/) because the URL contains a secret token which can be used by anyone to invoke your Jenkins job.
+ **GCHAT_WEBHOOK_SECRET_FILE** - This is the path to the secret file where the URL for the Google Chat's Incoming Webhook url is stored. It is ideal to pass Google Chat Webhook URL using [Docker Swarm Secrets](https://docs.docker.com/engine/swarm/secrets/) because the URL contains a secret token which can be used by anyone to send notifications to your Google Chat Room.
+ **GCHAT_WEBHOOK_ENDPOINT** - This is the endpoint using which is used by DTR to send a notification e.g. [www.example.com/abc](www.example.com/abc). If you call this URL with a JSON payload, it would deliver the JSON payload to your Google Chat room where Webhook has been setup. Make sure that this is complex enough 
+ **GCHAT_BOT_ENDPOINT** - This is the endpoint for Google Chat Bot e.g. [www.example.com/xyz](www.example.com/xyz). As recommended by Google, make sure that the end point is not a simple context path but a more complex one e.g. [www.example.com/qqlaysqhdsadasiqn](www.example.com/qqlaysqhdsadasiqn).
+ **DEBUG** - This defines whether the Python Flask app runs with ```debug=True``` or not. If you want to enable ```DEBUG mode```, set this to ```True``` or ```T``` or ```true```.

## Setup Google Chat
Once this code is up and running with a valid URL you can go ahead and setup your Google Chat bot and Google Chat's Incoming Webhook.
1. Setup Google Chat Bot *(WIP - a different Markdown file to be added for this)*
2. Setup Incoming Webhook for Google Chat room *(WIP - a different Markdown file to be added for this)*

## Setup DTR Repository

