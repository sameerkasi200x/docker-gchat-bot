# Setup Jenkins for Docker CI-CD

Jenkins is a popular tool used for build and deployment. It can help you automate trivial tasks in your SDLC process which in turn allows you to do those tasks more often resulting into better overall quality of the software. There are various plugins available which makes it easier to integrate with various other tools in your ecosystem. Plugins are also useful for defining a trigger point for a Jenkins job e.g. perform a build when someone checks-in code changes to Git repository. In the context of docker based development and deployment Jenkins can be used for:

1. Automating a ```docker build``` on code change
2. Perform new build when a new base image is available e.g. if you are running NodeJS application, you would want to rebuild it when new NodeJS image is available
3. Automate deployment of an image
4. Run/update a compose application when an image is pushed - for integration testing

In this example we will see how Jenkins can be used for:
1. Performing a build using Dockerfile and application code in GitHub repository
2. Performing a deployment using a docker image pushed to Docker 

## Setup and installation

Jenkins is a Java based application. That makes it portable across different platforms and easy to run. You need to ensure that Java is already installed. You can follow the [online documentation](https://jenkins.io/doc/pipeline/tour/getting-started/) to set it up. 
I prefer to use the [docker image provided by Jenkins team](https://hub.docker.com/r/jenkins/jenkins/). It is quite extensible and easy to use. I have a [half-baked Github project](https://github.com/sameerkasi200x/docker-jenkins) to extend the Jenkin image.

You can use the Dockerfile to create an image and create a Swarm or Kubernetes Service with that. You can also deploy the service with [Layer-7 routing](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/Docker-EE-setup.md#layer-7-routing) available in Docker EE 2.0.

## Setup Jenkins Slave
Once Jenkin's master is setup, we need to add a new slave where the jobs will be executed. The simplest way to add a new slave is to use ssh slave. To use an ssh slave, setup a new machine with Linux - a local VM, a Digitalocean Droplet, an Azure VM or a AWS EC2 instance. You can then setup [ssh key based authentication on the slave](https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server). Once the server is configured, you can go to Jenkins url and go to "Manage Jenkins" and then navigate to "Manage Nodes" as depicted in the diagram:

![Jenkins Manage Node](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-manage-node.png)

Click on "New Node" and then provide name of the node "Docker-build-slave" and add that as a "Permanent Agent". Then on the next page, add details for:

+ #of Executor:  This is the number of jobs that can concurrently run. Leave it to 1
+ Remote root directory: This is the directory which will be set as present working directory for the Jenkins job. For our case we need to set this to a directory where we will have Docker UCP client bundle setup. 
+ Label: If you want to add any label for your slave node
+ Usage: How much shall Jenkins master try to utilize this node for new jobs? Leave to default
+ Launch Method: This is important. Choose "Launch slave agents via ssh"
+ Host: The slave IP/hostname
+ Credentials: Click on "Add"--> "Jenkins" and [add a new credentials](https://jenkins.io/doc/book/using/using-credentials/#adding-new-global-credentials) where you will use the ssh key generated on the new slave machine. Once done, then come back and use this newly added Credential in your Node configuration.
+ Host key verification strategy: Choose how the host will be verified while doing an ssh. I am choosing "Non verifying verification strattegy" because I keep on adding nodes using EC2 and the IP/hostname gets repeated. It will avoid an error if the hostname & signature does not match what is stored in my Jenkins master node.

![Adding a new slave](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-add-slave.png)

Now click "Save"

Once the node is added, now you can login to the slave node and [download a UCP Client bundle](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-add-slave.png) on Jenkins slave you have just added. Make sure it is saved in the same directory that you supplied to "Remote root directory".

## Credentials
You have just now added a credential to Jenkins while adding a slave. You can navigate to credentials menu under "Manage Jenkins" and add a new credential of type username and password. The username will be the username for DTR and password will the password for the user. We will use this credential later in Job configuration.

## Jenkins Job - #1: Job for performing Docker Builds
Once Jenkins is installed and setup, you can go ahead and create a new Job to perform Docker build by going to below URL:

```http://<jenkins-url>>/view/all/newJob```

Enter a name for your Job e.g. ```docker-ci-cd``` and then choose type of project as "Freestyle Project" and press Ok.

Now you define details of various sections of job configuration as depicted below

### General

![Jenkins Job config - General](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-general.PNG)

### Source Code Management
Here you need to provide the details of your Git hub repository. Also ensure that this repository has been configured to use [Webhook to trigger a jenkins job](https://github.com/sameerkasi200x/docker-gchat-bot/blob/master/GitHub-repo-setup.md#setup-github-repository).

![Jenkins Job config - Source Code Management](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-src-code-mgmt.PNG)

### Build Trigger

This job is triggered using Github checkin.

![Jenkins Job config - Build Trigger](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-build-trigger.PNG)

### Build Environment

![Jenkins Job config - Build Env](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-build-env.PNG)

### Bindings
This is where we will use the Credential we created above for our DTR users. The username and password will be assigned to a variable so that it can be used in build steps.

![Jenkins Job config - Bindings](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-bindings.PNG)

### Build

You can use below as your build commands:

```
cd /home/centos/docker-ci-cd/ucp-bundle

eval "$(<env.sh)"
cd $WORKSPACE
docker build --pull=true -t dtr.example.com/admin/docker-ci-cd:$GIT_COMMIT  ./code
docker login --username $UCP_ADMIN_USER --password $UCP_ADMIN_PASSWD dtr.example.com
docker push dtr.example.com/admin/docker-ci-cd:$GIT_COMMIT
```

![Jenkins Job config - Build](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-config-build-steps.PNG)

Once the job has been setup, test it out by running it. The job here users GIT_COMMIT hash as the image tag. If your DTR repository is configured to be "Immutable" then you might need to do a dummy commit in Git Hub before every build. Otherwise the ```docker push``` command in Build phase would fail.

## Jenkins Job - #2: Job for performing deployment with Docker Service
This job will be used for deploying the latest image. Here it is very important that the GIT_COMMIT resulted in successful image build because this job will be using GIT_COMMIT (which will be obtained from Git Hub) to pull the latest image and deploy it using ```docker service udpate```. Also, ensure that the service being updated is already running.

Configure this job as per the instructions depicted in below pictures.

### General

![Jenkins Job config - General](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-2-config-general.PNG)

### Source Code Management
Here you need to provide the details of your Git hub repository. It should be the same repository which you have used in the previous job.

![Jenkins Job config - Source Code Management](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-2-config-src-code-mgmt.PNG)

### Build Trigger

This job is triggered by using Generic Webhook. We need to define the parameters which will be copied from the post content when the webhook is invoked remotely:

![Jenkins Job config - Webhook Triggered - Post content](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-2-config-build-trigger-1.PNG)

As this is invoked via a webhook (i.e. a REST call), you can additionally specicy header and request parameters. In my case I have kept them blank. Specify a token, we are using the default value. This should be complex enough as anyone with this token can trigger your job.

Enable Print post content & Print contributed variables

![Jenkins Job config - Webhook Triggered - more config](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-2-config-build-trigger-2.PNG)


### Build
You can use below as your build commands:

```
cd /home/centos/docker-ci-cd/ucp-bundle
eval "$(<env.sh)"
docker service update --detach=false --force --update-parallelism 1 --update-delay 30s --image dtr.example.com/admin/docker-ci-cd:$GIT_COMMIT  docker-ci-cd
```

Here ```docker-ci-cd``` is name of the service you have earlier deployed on UCP.

![Jenkins Job config - Build](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/jenkins-job-2-config-build-steps.PNG)

Once the job has been setup, test it out by running it.
