# Integrating Docker Trusted Registry with Google Chat

Google Recently launched Google Chat for GSuite users. Though it is far from perfect, I found it quite useful and hope that it would become a good alternative to Slack. It allows you to have DM (one-on-one) chat and create rooms (kind of group chat) - generalized as a [*SPACE*](https://developers.google.com/hangouts/chat/concepts/cards). You can add [Chat Bots](https://developers.google.com/hangouts/chat/concepts/bots) to these spaces to automate tasks like voting, create calendar invite, setup video call etc. You can also setup [Incoming Webhooks](https://developers.google.com/hangouts/chat/how-tos/webhooks) in spaces so that you can deliver messages to spaces by remotely invoking a URL.

I have tried to put together is a [simple Python code](https://github.com/sameerkasi200x/docker-gchat-bot/tree/master/code) to implement team integration/communication for Docker Trusted Registry with Google Chat Bot and Google Chat's Incoming Webhook. In its current form it can be useful to:

1. Send notifications in a Google Chat Room whenever a new image is pushed to Docker Trusted Registry. This uses [DTR's webhook features](https://docs.docker.com/ee/dtr/user/create-and-manage-webhooks/).
2. Deploy latest image using [Jenkins's Generic Webhook Trigger](https://wiki.jenkins.io/display/JENKINS/Generic+Webhook+Trigger+Plugin). This particular implementation just triggers a Jenkins build which internally knows how to get the latest image (by using the GIT_COMMIT). But it is quite easy to pass the image tag as the body of the JSON message passed by Chat Bot to Jenkins's webhook endoint.

![Build and Chat flow](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/Google%20Chat-Bot-for-Docker-Trusted-Registry-Draw.io.png)

The code is based on two examples provided by Google:
+ [Simple Chat Bot with Python & Flask](https://developers.google.com/hangouts/chat/how-tos/bots-develop)
+ [Incoming webhook with Python](https://developers.google.com/hangouts/chat/quickstart/incoming-bot-python)

## Setting up dependencies

This code depends on setup of [Docker Trusted Registry](https://docs.docker.com/ee/dtr/), GitHub and Jenkins. Once you setup this code, you should also enable [Google Chat API](https://developers.google.com/hangouts/chat/how-tos/bots-publish) and register the bot.

1. [Docker EE setup](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Docker-EE-setup.md)

2. [Jenkins Setup](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Jenkins-setup.md)

3. [GitHub repository setup](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/GitHub-repo-setup.md)

## Setting up sample bot code as a Docker Swarm Service

Before we can setup a Google Chat bot and webhook service we need to deploy the backend code as a handlers for both of them. This sample deploys the sample code as a service on Docker Universal Control Plane using Swarm orchestration. You can check out more details of [how Layer-7 Routing Mesh Works](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Docker-EE-setup.md#enable-layer-7-routing-in-ucp).

It is quite simple to enable [Layer-7 Routing in UCP](https://docs.docker.com/ee/ucp/interlock/deploy/). I have tried to cover the concept and deployment flow in more detail over [here](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Docker-EE-setup.md#enable-layer-7-routing-in-ucp).

The [code in this sample](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/code/flask_bot.py) deploys two handlers, both of which are deployed as secrets:

1. GCHAT_WEBHOOK_ENDPOINT: This environment variable is used to determine the end point for Webhook which will be configured and referred in Google Chat room. When configuring the webhook, we will need this value. It is recommended to use a long text with jumbled and un-reproduceable sequence of alphabets e.g. asadqweqndqwqeqwcxcnkj this value in turn would mean that your Webhook end point will be something like ```https://google-chat-bot.demoapps.example.com/asadqweqndqwqeqwcxcnkj```.

2. GCHAT_BOT_ENDPOINT: This environment variable is used to determine the end point for Google Chat bot which be configured in Google App API. It is recommended to use a long text with jumbled and un-reproduceable sequence of alphabets e.g. asadqweqndqwqeqwcxcnkj this value in turn would mean that your Google Chatbot end point will be something like ```https://google-chat-bot.demoapps.example.com/asadqweqndqwqeqwcxcxyz```.

The Dockerfile defines a few additional variables which are based on secret name defined while deploying the image:

1. GCHAT_WEBHOOK_SECRET_FILE: This environment variable is used to store the file name where the Webhook URL will be stored. You can define a secret and pass the path of secret in container to this variable. In the example compose file, a secret ```gchat_webhook ``` has been defined. This secret is used to store the url which is unique for an incoming Webhook for Google chat room. You can get this by enabling Webhook for a particular chat room where messages needs to be posted whenever an action is trigged. To enable an incoming Webhook, go to the chat room menu, select Configure Webhooks. 

![Webhook Configuration](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/Google-chat-Incoming-webhook-configuration-1.png)

A dialog appears that lists any incoming webhooks already defined for the room, you can define the new webhook over here:

![Webhook Configuration](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/Google-chat-Incoming-webhook-configuration-2.png)

You need to copy the URL for the Webhook and set that as the value of secret - ```gchat_webhook``` and pass ```/run/secrets/gchat_webhook``` as value of ```GCHAT_WEBHOOK_SECRET_FILE```.

2. JENKINS_URL_SECRET_FILE: This environment variable is used in Dockerfile to define the path of the file from where the URL for Jenkins Webhook will be fetched. In the compose file which is provided along with the code, a secret named ```jenkins_url``` has been defined. This secret is the URL of Jenkins webhook which will be called when Google Chat bot is triggered. The environment variable has been set to value ```/run/secrets/jenkins_url```.

For deploying this image as a swarm service with layer-7 routing, you also need to setup additional secrets which will store certificate and key for https communication.



Sample code to deploy this service

```
git clone https://github.com/sameerkasi200x/docker-gchat-bot.git
cd docker-gchat-bot/code
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
+ **GCHAT_WEBHOOK_ENDPOINT** - This is the endpoint using which is used by DTR to send a notification e.g. ```https://google-chat-bot.demoapps.example.com/abc```. If you call this URL with a JSON payload, it would deliver the JSON payload to your Google Chat room where Webhook has been setup. Make sure that this is complex enough e.g. ```asadqweqndqwqeqwcxcnkj```. The Webhook will be invoked by using the complete URL ```https://google-chat-bot.demoapps.example.com/asadqweqndqwqeqwcxcnkj```
+ **GCHAT_BOT_ENDPOINT** - This is the endpoint for Google Chat Bot e.g. ```google-chat-bot.demoapps.example.com/xyz```. As recommended by Google, make sure that the end point is not a simple context path but a more complex one e.g. ```google-chat-bot.demoapps.example.com/asadqweqndqwqeqwcxcxyz```. You only need to provide the context path here i.e. ```asadqweqndqwqeqwcxcxyz``` and not the whole URL
+ **DEBUG** - This defines whether the Python Flask app runs with ```debug=True``` or not. If you want to enable ```DEBUG mode```, set this to ```True``` or ```T``` or ```true```.

## Setup Google Chat
Once this code is up and running with a valid URL you can go ahead and setup your [Google Chat bot](https://developers.google.com/hangouts/chat/how-tos/bots-develop). Here you need to provide the bot-endpoint that you have configured.

Once it is setup, you can try to test Google chat bot by adding it to a chat-room (it is easier to use the same chatroom where incoming webhook was configured). You can invoke, it by sending a message ```@bot_name Deploy```. This should trigger a deployment using the [Jenkins job which you configured for updating the Docker Swarm service](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Jenkins-setup.md#jenkins-job---2-job-for-performing-deployment-with-docker-service).

![Google Chat bot example](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/google-chat-bot-example.PNG)

## Setup DTR Webhook
Once the code has been deployed, Incoming Webhook will be active. You need integrate it with you DTR by configuring the Webhook for a DTR repository. The [DTR webhook](https://docs.docker.com/ee/dtr/user/create-and-manage-webhooks/) is invoked on specific events e.g. scan completion, image push etc. Once the webhook is invoked, a message digest in JSON format is posted to the webhook. In our python code the webhook endpoint is configured to receive this JSON digest and post the scan summary to chat room.

To configure Webhook, open DTR URL in web browser and click on the repository for which you want to configure Webhook. Then click on "WEBHOOKS" tab and add new Webhook by clicking "New Webhook". A new input box will expand where you can provide the "Notification to receive" i.e the event which will trigger a call to Webhook and Webhook endpoint. 

![DTR Webhook](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/dtr-webhook.PNG)
Provide the values:

+ NOTIFICATION TO RECEIVE: Security scan completed
+ WEBHOOK URL: Here provide the URL with context path. The base URL will be as per the URL you have mapped to the service which is deployed using this code. The context path will be as per the GCHAT_WEBHOOK_ENDPOINT you have configured while deploying this code.

You can now test the incoming Webhook by triggering a Docker build using the [Jenkins job which configured to perform image builds](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Jenkins-setup.md#jenkins-job---1-job-for-performing-docker-builds). It should post a message in the chat-room.

![DTR Scan result posted to a chat room](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/dtr-scan-result-in-chat-room.PNG)

Now you can complete the flow where-in a code-checking will invoke a jenkins pipeline which would perform build of an image and push it to DTR. DTR in turn will invoke the Webhook configured in Google chat room to inform the administrator about the scan result of the newly pushed image. The administrator can then decide to deploy the image based on the scan summary. Admin can simply reply in the chat room to deploy the image : ```@chatBot deploy```.

## Contributing & Things to do
This is a simple project to demonstrate the flexibility offered by Docker EE platform and how it can be easily integrated with various other tools to build DevOps culture and more efficient automation pipelines. This is not meant for real production deployment but should give a fair idea to someone who plans to utilize these features of DTR to do production deployment. In an enterprise environment, you can easily replace Google Chat with another service e.g slack.

If you are intrested to make this code better, feel free to make a pull request to the [respository](https://github.com/sameerkasi200x/docker-gchat-bot). Code-wise few things which can be improvded:

1. Allow admin to choose an image tag in the message. Currently it relies on Integration between Github and Jenkins.

2. Handle corner cases where-in git code is updated and an image build is in progress and Admin says Deploy. As currently the image tag is fetched by Jenkins from Github (based on GIT COMMIT hash), this scenario would result into an error.

3. Because the scan result is too huge, I had to omit the scan and image layer details. It would be nice to iterate through the scan result dictionary and send all the details in the subsequent messages (after sending in the summary). 

4. Or may be allow Admin to ask for the details by saying "@bot get scan details". This would require integration with DTR API


