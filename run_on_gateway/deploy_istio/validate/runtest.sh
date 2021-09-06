#!/bin/bash
while true; do kubectl exec --context=$1 -n sample -c sleep "$(kubectl get pod --context=$1 -n sample -l \
        app=sleep -o jsonpath='{.items[0].metadata.name}')" -- curl -sS helloworld.sample:5000/hello; done