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

### 4. Test Client Bundle
Once you have the client bundle you can test basic swarm and Kubernetest (using kubectl) command against UCP cluster

```
docker node ls

docker container ls

```

### 5. Configure DTR

We need to change DTR configuration to enable vulnerability scanning. It is quite easy. You need to login to Docker Store (https://store.docker.com) using your Docker Hub account and download the CVE database. You will get a zip/tar.gz file. Go to dtr URL using FQDN of DTR node or the load balancer e.g.

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

### 6. Create A repository in DTR
Login to your dtr URL (this would be the FQDN of the worker node running DTR or the load-balancer and click on new repository
![DTR add repo](https://docs.docker.com/ee/dtr/images/create-repository-1.png)

Add name and details
![DTR add repo details](https://docs.docker.com/ee/dtr/images/create-repository-2.png)

Click on *Show advanced settings* and set **IMMUTABILITY** to ON and *SCAN ON PUSH* to **On push**.

### 7. Enable Layer-7 Routing in UCP


