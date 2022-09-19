FROM ubuntu:22.04

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV SRC_DIR="${HOME_DIR}/src"
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
    wget \
    g++-10 \
    plocate \
    ninja-build \
    lcov \
    gcovr \
    file

# prepares non root env
RUN useradd --create-home --shell /bin/zsh ${USER}
# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# end system level stuff
USER ${USER}

# install oh my zsh
RUN sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# install python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --user --upgrade -r /tmp/requirements.txt

## Conan
RUN mkdir ${BUILD_DIR}
# set up conan default profile
COPY --chown=${USER}:${USER} conan_profile.txt ${HOME_DIR}/.conan/profiles/default
COPY --chown=${USER}:${USER} conanfile.txt /tmp/conanfile.txt
RUN cd ${BUILD_DIR} && conan install /tmp/conanfile.txt -pr:b=default

# download the cmake gcov module to build directory
RUN wget https://raw.githubusercontent.com/bilke/cmake-modules/master/CodeCoverage.cmake -O ${BUILD_DIR}/CodeCoverage.cmake

# allow git from inside container
RUN git config --global --add safe.directory ${SRC_DIR}

# jupyter theme setup
RUN jt -t monokai -cellw 95%

# # add build dir to python path so bungee pybind module can be imported from anywhere
# ENV PYTHONPATH="${BUILD_DIR}:${PYTHONPATH}"

# working directory is the script dir for ease of dev since all primary development actions
# are in scripts
WORKDIR ${SRC_DIR}/scripts
