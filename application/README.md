## Deploying the facedetect example application

The services first need to be built and pushed to some container registry. For this we have assumed a registry hosted on gitlab, but other registries should work with low effort. First update the repository in the `apps/build_and_push.sh` script to point to a gitlab container registry that you can access. Run the script to build and push all necessary images.

```bash
chmod +x build_and_push.sh
./build_and_push.sh
```

Change the image in both `src/backend.yaml, src/frontend.yaml` to point to the correct registry/image.  

Check the `settings.py` file and choose which clusters to run the frontends and backends. Deploy the application with

```bash
python3 deploy.py
```

The deployment can be removed with

```bash
python3 remove.py
```

The application can be accessed at  `http://GATEWAY_IP/api` where images can be uploaded for face detection. 

#### Load generation

To generate load on the application, visit the `facedetect/load_generation` folder. Change the settings in `load_generator.py` and run it as

```
python3 load_generator.py
```



