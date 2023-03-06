#!/bin/bash

#VERSION=14.29.31
VERSION=16.1.5

cd molecalc/static/external

#wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%20${VERSION}/Jmol-${VERSION}-binary.zip
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2016.1/Jmol%20${VERSION}/Jmol ${VERSION}/Jmol-${VERSION}-binary.zip

unzip Jmol-${VERSION}-binary.zip

cd jmol-${VERSION}
unzip jsmol.zip

cd ..

mv jmol-${VERSION}/jsmol jsmol

rm -r jmol-${VERSION}
rm Jmol-${VERSION}-binary.zip

