#!/bin/bash

cd molecalc/static/external

VERSION=5.8.2

wget https://use.fontawesome.com/releases/v$VERSION/fontawesome-free-$VERSION-web.zip

unzip fontawesome-free-$VERSION-web.zip

rm -r fontawesome
mv fontawesome-free-$VERSION-web fontawesome
rm fontawesome-free-$VERSION-web.zip

