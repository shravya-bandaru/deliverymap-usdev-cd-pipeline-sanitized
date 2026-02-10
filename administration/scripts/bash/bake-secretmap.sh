#!/bin/bash
while getopts s:p: flag
do
    case "${flag}" in
        s) secret=${OPTARG};;
        p) path=${OPTARG};;
    esac
done
cd $path
cat <<EOF
secretGenerator:
- name: $secret
  files:
EOF
for i in *; 
do
cat <<EOF
  - envs/$i
EOF
done
cat <<EOF
generatorOptions:
    disableNameSuffixHash: true
EOF
