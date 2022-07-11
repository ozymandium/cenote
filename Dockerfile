FROM ubuntu:20.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV SRC_DIR="${HOME_DIR}/src"
ENV DEP_DIR="${HOME_DIR}/dep"
ENV BUILD_DIR="${HOME_DIR}/build"
ENV PATH="${HOME_DIR}/.local/bin:${PATH}"

# configures locale
RUN apt update -qq > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt install -qq --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

# system requirements to build most of the recipes
RUN apt update -qq > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt install -qq --yes --no-install-recommends \
    build-essential \
    cmake \
    ccache \
    git \
    python3-dev \
    python3-pip \
    sudo \
    zsh \
    ranger \
    curl \
    vim \
    wget

# prepares non root env
RUN useradd --create-home --shell /bin/zsh ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}
WORKDIR ${SRC_DIR}

# install oh my zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --user --upgrade -r /tmp/requirements.txt

## dependencies of c++ stuff
RUN mkdir ${DEP_DIR}

# install units library
RUN wget https://github.com/nholthaus/units/archive/refs/tags/v2.3.1.tar.gz -O /tmp/units.tar.gz
RUN tar -xf /tmp/units.tar.gz -C ${DEP_DIR}
RUN mkdir ${DEP_DIR}/units-2.3.1/build
RUN cd ${DEP_DIR}/units-2.3.1/build && cmake .. && sudo make -j4 install

# allow git from inside container
RUN git config --global --add safe.directory ${SRC_DIR}

# build the library
RUN mkdir ${BUILD_DIR}
