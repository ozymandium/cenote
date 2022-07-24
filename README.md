cenote
======

Scuba decompression model explorer.

This is not good, it's probably not even right, so don't use it to plan your dives.
If you ignore this advice and get yourself bent or killed, that's not my problem.

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
