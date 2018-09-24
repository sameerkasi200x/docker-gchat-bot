# Setup GitHub Repository 

We need to setup a Github repository for hosting code for your application service. I am using my sample [docker-ci-cd repository](https://github.com/sameerkasi200x/docker-ci-cd) for this setup. You can simple go to Github and fork it:

![Fork Github repo](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/github-fork-repo.png)

Or you can create a new GitHub repo.

Once the repo is in place, you need to enable integration with Jenkins. To do the same, we have two options:

+ Webhooks - To follow this method, your Jenkins pipeline/job should be allowed to triggered by ```Generic Webhook Trigger```. In case you plan to integrate Jenkins and GitHub using Webhooks, you can add a Generic Webook (using URL obtained from Jenkins and ```application/json``` as content type).

+ Integration & Services -  To follow this method, your Jenkins pipeline/job should allowed to be triggered by ```GitHub hook trigger for GITScm polling```. Rest of this document will follow this method.

1. Go to **Settings** Tab--> Click on **Integrations & Services** menu on left hand side--> Click on **Add Service** drop down --> Select **Jenkins (GitHub Plugin)**

![Github-Jenkins integration](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/github-service-integration.png)

2. Add URL for Jenkins repo and click **Add Service**
![Add Jenkins URL for GitHub Integration](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/github-service-integration-step-2.png)

Try to perform a commit to GitHub and see if that triggers the Jenkins Job or not. If the job is not getting triggered then there is some issue with your configuration. Please revist and carefully evaluate the config changes you did just now to enable the integration.


### Use GIT_COMMIT as image tag
If the integration works, then you need to edit the job which gets triggered by GitHub check-in i.e. the Job responsible for building a new image and pushing it to GitHub. Edit the job to change the image tag in ```docker build ``` and ```docker push``` commands to use ```$GIT_COMMIT```.

So the docker build command would be something like:

```docker build --pull=true -t dtr.example.com/admin/docker-ci-cd:$GIT_COMMIT  ./code```

And the docker push command will be

```docker push dtr.example.com/admin/docker-ci-cd:$GIT_COMMIT```
