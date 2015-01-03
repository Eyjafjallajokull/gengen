# GenGen

This project aims to build 3d model using only 2d grayscale image as reference. It is impossible to make a real, accurate 3d model, what I'm trying to achieve is an *abstract* model. The result of an algorithm will be a model consiting of many triangles, looking at it from specified direction and with proper lighting should reveal base image. From any other direction model will look like randomly placed triangles.

# Current status

At this moment algorithm is able to generate models for very simple shapes, and is very, **very** slow.

## How?

* Using genetic algorithm with tournament selection.

## Example

* base image
* result image
* 3d model screen
* time, generations, renders, config

## Requirements

sudo apt-get install blender
pip install pyyaml