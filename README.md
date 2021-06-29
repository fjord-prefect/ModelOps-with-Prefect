# ModelOps-with-Prefect

This is an poc suggestion of a way to implement the start of a CI/CD/CT process.  I chose Prefect because it's the lowest overhead and easiest to get started of the MLOps tools out there eg Airflow, Kubeflow etc.  I'm not a proponent of prefect despite my github handle.  I'd actually choose Airflow over Prefect due to its larger user base and tutorials for different non-template use cases are more readily available.

# The Example
The example model I chose is an object detect model which uses Joseph Redmon's You Only Look Once model architecture to predict bounding box coordinates of dogs in images.  Basically it predicts where a dog is in an image by drawing a box around it.  I've hard coded scripts.utils to only pull 3 images of dogs from coco so if you'd actually want to train a good model you'll have to alter line 42 in scripts/utils.py.  This will download about 5000 images of dogs if you let it.

# Host Dependencies
You will need python 3.6, docker, and prefect which are the only dependencies for your host machine.  This workflow can be run on windows, mac or linux; however, setting up docker and python 3.6 will vary depending on your host machine.  I recommend using conda to set up a python environment and to install docker follow the instructions here https://www.docker.com/get-started.

Assuming you have docker and conda already installed here are the step by step instructions and will work for any host os.

Clone the directory.
```dif
git clone https://github.com/fjord-prefect/ModelOps-with-Prefect.git
cd ModelOps-with-Prefect
```

Create an environment called threesix which has python 3.6 installed and activate it.
```dif
conda create -n threesix python=3.6
conda activate threesix
```

You should now see the text "(threesix)" in your command prompt.  
Test it out by running 
python -V
The output should look like:  Python 3.6.13 :: Anaconda, Inc.

# Set up Prefect Server
Open a separate terminal window.
You may need root access for docker commands in linux and I'm still sorting out some path issues.  So if you are on linux make sure your python path is in your /etc/sudoers file.  If you're on Windows it doesn't matter.

Now install prefect
```dif
conda activate threesix
pip install prefect
```

boot up the prefect server
```dif
$prefect backend server
$prefect server start
```

This is going to build a docker image for the prefect server and start running the prefect server conatiner.   

Woohoo we have our prefect server running but it doesn't know about any of our code.  So open a new terminal window.  After this is finished you can inspect the image by typing $docker images.  You can also inspect the running container with $docker ps and the UI by typing localhost:8080 into your browser. 

Now go to localhost:8080 in your browser and click the project tab and start a new project and name it monster_mash.

# Set up Prefect Agent
Okay now before we can run our code in prefect we need to set up an agent to communicate our code to the prefect server.  Open a new terminal window.
```dif
conda activate threesix
prefect agent docker start --volume \<insert path on your computer to dir\>/ModelOps-with-Prefect/local_feature_store:/home/local_feature_store --label feature_store --show-flow-logs
```
This step is important. During the flow run a directory local_feature_store and a directory volume will be created.  The --volume tag sets up a bind mount with the local_feature_store on your computer located in the ModelOps-with-Prefect directory and the docker image directory.  During the container run the model will download images and output model metrics and predictions to this directory which because you set up the bind mount will also show up on your local machine.  The second --volume tag creates a named volume that persists within docker.  This persisting directory can be mounted to any container share across registries etc.
  
# Build the Execution Image
Now we need a docker image that has the dependencies to run our actual modoel code so open another terminal.  cd to the ModelOps-with-Prefect directory.  Make sure you're in the right conda environment.

Build the docker image
```dif
conda activate threesix
docker build . -t fjord_prefect:1
```
If you have issues with this step.  First make sure you are in the ModelOps-with-Prefect directory.  When you run ls there should be a file called Dockerfile in the directory.  Next make sure you are in the correct conda environment with the command $conda activate threesix.  When you run python -V you should get Python 3.6.  

The command $docker build . is just telling docker to look for this Dockerfile within the current directory and build an image based on the instructions inside the Dockerfile.  The -t flag is tagging this image fjord_prefect:1 so we can refer to it later.

This will take a few minutes to build.  There are strategies to minimize build time during development that I will touch on later.  We can inspect our image with the following command $docker images.  It should look something like this.  These are all blue prints or "images" for docker containers.  All we did was build the blueprint of our python code.

REPOSITORY              TAG            IMAGE ID       CREATED         SIZE
fjord_prefect           1              8fb04c2c88bc   2 minutes ago   3.6GB
python                  3.6            b58bb3901b01   14 hours ago    875MB
postgres                11             7629fb0a5b77   6 days ago      283MB
prefecthq/ui            core-0.14.22   daa5219a276a   3 weeks ago     194MB
prefecthq/server        core-0.14.22   e9ea2f58c4f6   4 weeks ago     398MB
prefecthq/apollo        core-0.14.22   eb0ed8596e5e   4 weeks ago     320MB

A container is the running version of an image.  The container is its own operating system isolated from the host machine but using its memory and cpu etc.  To see what containers are running use the command $docker ps

Here you can see all of our prefect server containers running and the images they are using as blueprints.  So we still haven't ran any of our code.  This has all been set up to now.  Lets recap all of our windows we have open and steps up until now.  We have:

(1) a running prefect server 
(2) a running prefect agent ...in our python3.6 environment that we're calling "threesix"...
(3) a built docker image that we tagged fjord_prefect:1 ...this has all our code and ML dependencies...

# Register your Flow

Now lets actually train the model and run a prefect flow.  

Open a new terminal window:

```diff
conda activate threesix
cd <some_path_...>/ModelOps-with-Prefect
python fjord_flow.py
```

# Run your Flow through the UI
Now the code and image are registered as a flow under the flows tab in the UI.  You can now run this flow through the UI which will spin up the docker container fjord_prefect:1 and run your code and all the dependencies on that docker container.  You can track run metrics etc.  The output from the run will be located in your local_feature_store directory in ModelOps-with-Prefect.  It will also be located in a docker volume that can be accessed and used by other docker containers.
