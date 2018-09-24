# Configuration of Docker EE Platform

## Install and Setup Docker EE

You can follow the online Docker documentation to install and configure Docker EE:
1. [Install Docker Universal Control Plane](https://docs.docker.com/ee/ucp/admin/install/). Once the installation is done, acces the UCP portal using the FQDN of the maanger node and install docker EE license. You can obtain a trial license by logging-in to the [Docker Store](https://store.docker.com) and download your trial license and upload that by going to UCP admin settings.

2. [Add worker (and optionally manager) nodes to UCP](https://docs.docker.com/ee/ucp/admin/configure/join-nodes/join-linux-nodes-to-cluster/) 

3. [Docker Trusted Registry](https://docs.docker.com/ee/dtr/admin/install/) on UCP cluster. Optionally [setup HA for DTR](https://docs.docker.com/ee/dtr/admin/configure/set-up-high-availability/) and [change the storage backend for the DTR](https://docs.docker.com/ee/dtr/admin/configure/external-storage/).

4. The DTR setup uses self-signed certificates, so we need to configure Docker UCP worker nodes to trust DTR. You can follow [this online documentation](https://docs.docker.com/ee/dtr/user/access-dtr/) to download DTR certificate and add that to list of trusted authorities on all worker nodes.

## Download and setup UCP Client Bundle
Once you have installed the UCP and DTR, download UCP Client Bundle on a machine which has docker client installed by following these instructions:

### 1. Setup environment variables on docker client node

Ensure that the UCP is setup using certificate with all manager nodes and load balancer as part of SAN. You can simply use self-signed certificate that UCP would install out of the box during install phase. You can set up the SANs when you install UCP with the ```--san``` argument. You can also [add them after installation](https://docs.docker.com/ee/ucp/admin/configure/add-sans-to-cluster/#add-new-sans-to-ucp).

```
export ucp_user=admin ##Set to the actual username which you used during the ucp install command
export ucp_password=ucp_admin_password ## Set this to the password provided in ucp install command or keyed-in during interactive installation
export ucp_address=ucp_manager_node_name[:port]  ## Set this to the FQDN of the manager node or set this to FQDN by which the load-balancer is identified. Optionally also include the port if UCP is not listening on default 443 port.
```

### 2. Get a new auth token
```
export AUTHTOKEN=$(curl -sk -d '{"username":"'"${ucp_user}"'","password":"'"${ucp_password}"'"}' https://${ucp_address}/auth/login | awk -F "\"" '{print $4}');

echo $AUTHTOKEN 
```


You should see a valid auth token as an output of second command here. If you don't see that, then try to debug the first command. Sample output:

```
$ echo $AUTHTOKEN
7c52261f-233b-492b-8494-8c651d2a1371
```

### 3. Download and setup Client Bundle

```
curl -k -H "Authorization: Bearer $AUTHTOKEN" https://${ucp_address}/api/clientbundle -o client-bundle.zip;
unzip client-bundle.zip;
eval "$(<env.sh)";
```

## Test Client Bundle
Once you have the client bundle you can test basic swarm and Kubernetest (using kubectl) command against UCP cluster

```
docker node ls

docker container ls

```

## Configure DTR

We need to change DTR configuration to enable vulnerability scanning. It is quite easy. You need to login to [Docker Store](https://store.docker.com) using your Docker Hub account and download the CVE database. You will get a zip/tar.gz file. Go to dtr URL using FQDN of DTR node or the load balancer e.g.

[https://dtr.example.com/system/settings/security](https://dtr.example.com/system/settings/security)

And then click on *ENABLE SCANNING* and upload the CVE database. If you docker node running DTR has internet connection, you can also choose to get CVE database **ONLINE**

If you are facing any problem [docker documentation](https://docs.docker.com/ee/dtr/admin/configure/set-up-vulnerability-scans/) has detailed section on making this change.

You should also consider changing confiruation to allow creation of a new repository on push. You can do it by using DTR API:

```
export ADMIN_USER=admin ## Change as per the admin username provided during UCP installation

export ADMIN_PASSWORD=password-for-admin-user 

export $DTR_URL=https://url-dtr[:port]   ### e.g. https://dtr.example.com

curl --user $ADMIN_USER:$ADMIN_PASSWORD \
--request POST "${DTR_URL}/api/v0/meta/settings" \
--header "accept: application/json" --insecure \
--header "content-type: application/json" \
--data "{ \"createRepositoryOnPush\": true}"
```

You can also do this from DTR web console by going to General Settings section

[https://dtr.example.com/system/settings/general](https://dtr.example.com/system/settings/general)

Go to the section for *Repositories* and enable *CREATE REPOSITORY ON PUSH*.

## Create A repository in DTR
Login to your dtr URL (this would be the FQDN of the worker node running DTR or the load-balancer) and click on new repository
![DTR add repo](https://docs.docker.com/ee/dtr/images/create-repository-1.png)


Add name and details and then click on *Show advanced settings* and set **IMMUTABILITY** to ON and *SCAN ON PUSH* to **On push**.


![DTR add repo details](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/dtr-repo-creation.PNG)


## Enable Layer-7 Routing in UCP

## Swarm Routing Mesh
Docker engine running in swarm mode (or with UCP cluster) offers routing mesh which makes it easier for you to expose service to the users and other services which are outside your Docker Cluster. Routhing mesh enables an internal load-balancer and allows every node to listen for the exposed port. Hence user traffic can be routed to any of the nodes and it will be internally routed to the swarm service.


![Swarm Routing Mesh](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/Swarm-Routing-Mesh.png)


### Layer-7 Routing
One of the limitations with Swarm Routing Mesh is with respec to opening up ports and availability of ports. Once you start rolling out more and more services, you will be restricted by the number of ports you can afford to map and open up every port (that you map to a swarm service) in your firewall. UCP helps you overcome this limitation with layer 7 layer routing, allowing users to access Docker services using domain names instead of IP addresses. Domain names are mapped to service containers by using an internal proxy service (called Interlock Proxy - ucp-interlock-proxy). The proxy service is updated whenever you deploy a new serivce. This (config update) is handled by another service called Interlock Extension(ucp-interlock-extension). Interlock Extension service receives updates about new events from the main service called Interlock (ucp-interlock).


![Layer 7 Routing with UCP](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/UCP-Layer-7-Routing-Interlock.png)


### Benefits
Main advantages of using UCP Interlock proxy/Layer 7 Routing:

+ **High availability:** All the components used for layer 7 routing leverage Docker swarm for high availability, and handle failures gracefully.

+ **Automatic configuration:** UCP monitors your services and automatically reconfigures the proxy services so that everything handled for you.

+ **Scalability:** You can customize and tune the proxy services that handle user-facing requests to meet whatever demand your services have.

+ **TLS:** You can leverage Docker secrets to securely manage TLS Certificates and keys for your services. Both TLS termination and TCP passthrough are supported.

+ **Context-based routing:** You can define where to route the request based on context or path.
Host mode networking: By default layer 7 routing leverages the Docker Swarm routing mesh, but you don’t have to. You can use host mode networking for maximum performance.

+ **Security:** The layer 7 routing components that are exposed to the outside world run on worker nodes. Even if they get compromised, your cluster won’t.


### Enable Layer-7 Routing with Interlock in UCP
To enable Layer-7 routing, you need to login to UCP web-console and nagivate to 

"Admin Settings-->Layer 7 Routing"

Or simple go to the URL:

[https://ucp.example.com/manage/settings/interlock](https://ucp.example.com/manage/settings/interlock)

Change the port if needed and enable Layer 7 Routing:


![UCP Layer 7 Routing Configuration](https://raw.githubusercontent.com/sameerkasi200x/docker-gchat-bot/master/images/UCP-Layer-7-Routing-configuration-snapshot.PNG)


### Understanding Deployment Life Cycle
Once the layer 7 routing service is enabled, you apply specific labels to your swarm services. The labels define the hostnames that are routed to the service, the ports used, and other routing configurations.

Once you deploy or update a swarm service with those labels:

1. The ucp-interlock service is monitoring the Docker API for events and publishes the events to the ucp-interlock-extension service.

2. That service in turn generates a new configuration for the proxy service, based on the labels you’ve added to your services.

3. The ucp-interlock service takes the new configuration and reconfigures the ucp-interlock-proxy to start using it.

If the hostname or the network is not properly configured, you will get ```502- Bad Gateway error``` when you try to access the network.


### Example Deployment
When you deploy a service which needs to be mapped to a domainname/hostname by leveraging Interlock, you need to provide:

1. hostname by which the service will be identified: ```com.docker.lb.hosts```
2. port number on which the service is exposed with-in container: ```com.docker.lb.port```
3. network name on which service is attached: ```com.docker.lb.network```

```
### Create the overlay network for application service
docker network create --driver=overlay tweet-nw

### Deploy application service with service lable for Interlock to pickup
docker service create --network ucp-interlock --name tweet-to-us --mode replicated \
        --replicas 2 \
        --label com.docker.lb.hosts="tweet.apps.example.com" \
        --label com.docker.lb.network="tweet-nw" \
        --label com.docker.lb.port="80" \
        --constraint 'node.platform.os==linux' \
        --detach=true \
        $dtr_url/development/tweet-to-us:b1
```

Reference:
[1] [Official Docker Documentation o Interlock as Layer-7 Routing Mesh](https://docs.docker.com/ee/ucp/interlock/architecture/#deployment-lifecycle)
