#!/bin/bash

mkdir -p figures
mkdir -p models
mkdir -p models/NRLEE

rm -fr models/NRLEE/*
rm figures/*

curl -J -L -o models/NRLEE/model7.tar.gz https://osf.io/2t6fy/download
curl -J -L -o models/NRLEE/model8.tar.gz https://osf.io/ev2cj/download
curl -J -L -o models/NRLEE/model9.tar.gz https://osf.io/a3jbs/download

curl -J -L -o figures/nrlee-anatomy.pdf https://osf.io/zerch/download

cd models/NRLEE
for model in model7 model8 model9
do
    tar zxvf $model.tar.gz
done

cd ../../python

python master.py
