#!/bin/bash

#VERSION=14.29.31
#VERSION=16.1.5   # Current version running on AWS
#VERSION=16.1.57  # Latest version of JSmol that appears to work (mostly) as expected
#VERSION=16.1.63  # Doesn't work (calculation "Tabs" other than Thermochemistry don't load JSmol viewer)
#VERSION=16.2.7   # Doesn't work (calculation "Tabs" other than Thermochemistry don't load JSmol viewer)

MAJOR=16
MINOR=1
PATCH=57

VERSION=${MAJOR}.${MINOR}.${PATCH}

cd molecalc/static/external

#wget https://sourceforge.net/projects/jmol/files/Jmol/Version%20${MAJOR}.${MINOR}/Jmol%20${VERSION}/Jmol-${VERSION}-binary.zip
#wget https://sourceforge.net/projects/jmol/files/Jmol/Version%20${MAJOR}.${MINOR}/Jmol%20${VERSION}/Jmol ${VERSION}/Jmol-${VERSION}-binary.zip
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%20${MAJOR}.${MINOR}/Jmol%20${VERSION}/Jmol-${VERSION}-binary.zip

unzip Jmol-${VERSION}-binary.zip

cd jmol-${VERSION}
unzip jsmol.zip

cd ..

mv jmol-${VERSION}/jsmol jsmol

rm -r jmol-${VERSION}
rm Jmol-${VERSION}-binary.zip


