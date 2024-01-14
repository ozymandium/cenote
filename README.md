cenote
======

<img src="resources/icons/cenote.png" width=200/>

Scuba decompression model explorer with a focus on gas planning for the special considerations of cave dives.

This is purely a toy, so don't use it to plan your dives.
I make no guarantees on the reliability of this software right now.
Technical diving and diving in overhead environments is dangerous, requiring advanced skills and training.
DO NOT USE THIS TO PLAN YOUR DIVE.
If you ignore this advice and get yourself bent or killed, that's your fault.

## Setup

Install docker and run the container:

```
./scripts/docker
```

Within the docker container, compile and test everything:

```
./build && ./test
```

Now you are ready to plan a dive and examine tissue compartment behavior. 
From your host machine, do:

```
./scripts/jupyter
```

Open up the jupyter notebook at the link that is printed, and you're good to go.

## Development

Code conventions: `./lint` in the container.

Code coverage is a WIP.
