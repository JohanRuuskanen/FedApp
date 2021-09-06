#!/usr/bin/env bash

export GITLAB_REGISTRY= # Insert registry here
export REGPATH= # Insert path to container here

docker login $GITLAB_REGISTRY

for d in */ ; do
    docker build -t $GITLAB_REGISTRY/$REGPATH/"${d///}" $d.
    docker push $GITLAB_REGISTRY/$REGPATH/"${d///}"
done
