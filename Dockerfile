FROM ubuntu:20.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV SRC_DIR="${HOME_DIR}/src"
ENV WORK_DIR="${SRC_DIR}/app" \
    PATH="${HOME_DIR}/.local/bin:${PATH}"

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
    # autoconf \
    # automake \
    build-essential \
    # ccache \
    cmake \
    # gettext \
    git \
    # libffi-dev \
    # libltdl-dev \
    # libssl-dev \
    # libtool \
    # openjdk-13-jdk \
    # patch \
    # pkg-config \
    python3-pip \
    python3-setuptools \
    sudo \
    # unzip \
    # zip \
    # zlib1g-dev \
    zsh \
    ranger \
    # python3.8-venv \
    # curl

# prepares non root env
RUN useradd --create-home --shell /bin/zsh ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}
WORKDIR ${WORK_DIR}

# install oh my zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install app dependencies
COPY lib/requirements.txt /tmp/requirements.txt
RUN pip3 install --user --upgrade -r /tmp/requirements.txt
