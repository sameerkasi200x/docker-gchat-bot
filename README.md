## Docker Google Chat Bot

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

