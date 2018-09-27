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

