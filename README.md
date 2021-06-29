# ModelOps-with-Prefect

You will need python 3.6, docke, and prefect which are the only dependencies for your host machine.  This workflow can be run on windows, mac or linux; however, setting up docker and python 3.6 will vary depending on your host machine.  I recommend using conda to set up a python environment and follow the instructions on docker https://www.docker.com/get-started.

Assuming you have docker and conda already installed here are the step by step instructions and will work for any host os.

First create an environment called threesix which has python 3.6 installed.
#conda create -n threesix python=3.6

Activate the environment threesix.  
# conda activate threesix
You should now see the text "(threesix)" in your command prompt.  
Test it out by running 
python -V
The output should look like:  Python 3.6.13 :: Anaconda, Inc.

Open a separate terminal window.
You may need root access for docker commands.  If you are on linux you can use sudo -i to log into root terminal.  Windows takes care of this during the install so it shouldn't be an issue.

Now install prefect
# pip install prefect

boot up the prefect server
# prefect backend server
# prefect server start

This is going to build a docker image for the prefect server and start running the prefect server conatiner.   

Woohoo we have our prefect server running but it doesn't know about any of our code.  So lets leave that terminal up and running and open a new terminal window.  After this is finished you can inspect the image by typing $docker images.  You can also inspect the running container with $docker ps and the UI by typing localhost:8080 into your browser. 

Okay now before we can run our code in prefect we need to set up an agent to communicate our code to the prefect server.  Open a new terminal window.  You will need admin rights on this one so sudo -i if you're on linux.

prefect agent docker start

Now we need a docker container to run our actual python code so open another terminal.  cd to the ModelOps-with-Prefect directory.  Make sure you're in the right conda environment.
# conda activate threesix

And build the container.  Exclude the sudo if you are on windows.
sudo docker build . -t fjord_prefect:1

So if you have issues with this step.  First make sure you are in the ModelOps-with-Prefect directory.  When you run ls there should be a file called Dockerfile in the directory.  Next make sure you are in the correct conda environment with the command $conda activate threesix.  When you run python -V you should get Python 3.6.  

The command $docker build . is just telling docker to look for this Dockerfile and build an image based on the instructions inside the Dockerfile.  The -t flag is tagging this image fjord_prefect:1 so we can refer to it later.

Okay this will take a few minutes to build.  There are strategies to minimize build time during development that I will touch on later.  We can inspect our image with the following command $docker images.  It should look something like this.  These are all blue prints or "images" for docker containers.  All we did was build the blueprint of our python code.

REPOSITORY              TAG            IMAGE ID       CREATED         SIZE
fjord_prefect           1              8fb04c2c88bc   2 minutes ago   3.6GB
python                  3.6            b58bb3901b01   14 hours ago    875MB
postgres                11             7629fb0a5b77   6 days ago      283MB
prefecthq/ui            core-0.14.22   daa5219a276a   3 weeks ago     194MB
prefecthq/server        core-0.14.22   e9ea2f58c4f6   4 weeks ago     398MB
prefecthq/apollo        core-0.14.22   eb0ed8596e5e   4 weeks ago     320MB

A container is the running version of an image and is its own little operating system isolated from the host machine but using it memory and cpu etc.  To see what containers are running use the command $docker ps

(threesix) dead4taxreasons@dead4taxreasons:~/Desktop/test/ModelOps-with-Prefect$ sudo docker ps
CONTAINER ID   IMAGE                           COMMAND                  CREATED          STATUS                    PORTS                                               NAMES
8ebfb15e111a   prefecthq/ui:core-0.14.22       "/docker-entrypoint.…"   24 minutes ago   Up 24 minutes (healthy)   80/tcp, 0.0.0.0:8080->8080/tcp, :::8080->8080/tcp   tmp_ui_1
4f0f181d9c44   prefecthq/apollo:core-0.14.22   "tini -g -- bash -c …"   24 minutes ago   Up 24 minutes (healthy)   0.0.0.0:4200->4200/tcp, :::4200->4200/tcp           tmp_apollo_1
b0437fdbc557   prefecthq/server:core-0.14.22   "tini -g -- python s…"   24 minutes ago   Up 24 minutes                                                                 tmp_towel_1
fa3e7455b4f3   prefecthq/server:core-0.14.22   "tini -g -- bash -c …"   24 minutes ago   Up 24 minutes (healthy)   0.0.0.0:4201->4201/tcp, :::4201->4201/tcp           tmp_graphql_1
ebfa2cb62152   hasura/graphql-engine:v1.3.3    "graphql-engine serve"   24 minutes ago   Up 24 minutes (healthy)   0.0.0.0:3000->3000/tcp, :::3000->3000/tcp           tmp_hasura_1
66e6897ab1a6   postgres:11                     "docker-entrypoint.s…"   24 minutes ago   Up 24 minutes (healthy)   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp           tmp(threesix) 

Here you can see all of our prefect server containers running and the images they are using as blueprints.  So we still haven't ran any of our code!  This all been set up to now.  Let recap all of our windows we have open and steps up until now.  We have:

(1) a running prefect server 
(2) a running prefect agent ...in our python3.6 environment that we're calling "threesix"...
(3) a built docker image that we tagged fjord_prefect:1 ...this has all our code and ML dependencies...

Now lets actually train this model and run a prefect flow.  

Open a new terminal window:
# conda activate threesix
# cd <some_path_to_ModelOps-with-Prefect>/ModelOps-with-Prefect
# python fjord_flow.py

