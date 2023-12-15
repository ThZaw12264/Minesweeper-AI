#!/bin/bash

rm -rf Problems
mkdir Problems
 
python3 WorldGenerator.py 100 Beginner_world_ 8 8 10

python3 WorldGenerator.py 100 Intermediate_world_ 16 16 40

python3 WorldGenerator.py 100 Expert_world_ 16 30 99

echo Finished generating worlds!
