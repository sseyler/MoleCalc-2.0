#!/bin/bash

VERSION=3.4.1

cd molecalc/static/external
mkdir -p jquery

wget https://code.jquery.com/jquery-$VERSION.min.js

mv jquery-$VERSION.min.js jquery/jquery.min.js
touch jquery/jquery.min.js




