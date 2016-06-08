#!/bin/bash

echo "Enter commit message: "
read msg

git add .
git commit -m "$msg"
git push -u origin master
