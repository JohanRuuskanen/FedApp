## Deploying the facedetect example application

The services first need to be built and pushed to some container registry. For this we have assumed a registry hosted on gitlab, but other registries works as well. First update the repository in the `apps/build_and_push.sh` script to point to a gitlab container registry that you can access. Run the script to build and push all necessary images.

```bash
chmod +x build_and_push.sh
./build_and_push.sh 
```

Change the image in both `src/backend.yaml, src/frontend.yaml` to point to the correct registry/image. 

Deploy the application with

```bash
python3 deploy.py
```

The deployment can later be removed with

```bash
python3 remove.py
```

The application can be reached on port 3001 on the gateway, and to access it simply perform a port-forward using e.g. ssh `ssh -L 3001:localhost:3001 ubuntu@GATEWAY_IP` and then visit `http://localhost:3001` on your local computer. 

#### Load generation

To generate load on the application, visit the `facedetect/load_generation` folder. 

First download e.g. the UMass face detection database <http://vis-www.cs.umass.edu/fddb/> and extract it to a `application/data` folder on the gateway. 

Then run the load generation as

```
python3 run_experiment.py
```
