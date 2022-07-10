FROM ubuntu:20.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV SRC_DIR="${HOME_DIR}/src"
ENV DEP_DIR="${HOME_DIR}/dep"
ENV WORK_DIR="${SRC_DIR}" \
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
    build-essential \
    cmake \
    ccache \
    git \
    python3-pip \
    python3-setuptools \
    sudo \
    zsh \
    ranger \
    curl \
    vim \
    wget \
    libfmt-dev \
    g++-10

# prepares non root env
RUN useradd --create-home --shell /bin/zsh ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER ${USER}
WORKDIR ${WORK_DIR}

# install oh my zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --user --upgrade -r /tmp/requirements.txt

# RUN mkdir ${DEP_DIR}
# COPY cpp_installs.sh /tmp/cpp_installs.sh
# RUN sh /tmp/cpp_installs.sh ${DEP_DIR}
