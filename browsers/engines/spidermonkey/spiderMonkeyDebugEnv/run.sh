#!/bin/bash

docker run --rm --privileged --security-opt=apparmor:unconfined -ti spidermonkey:latest $1
