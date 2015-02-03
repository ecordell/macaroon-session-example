FROM ubuntu:trusty
MAINTAINER Evan Cordell <cordell.evan@gmail.com>

## Prepare
RUN apt-get clean all
RUN apt-get update
RUN apt-get upgrade -y

# Build Tools
RUN apt-get install -y build-essential zlib1g-dev libssl-dev libreadline6-dev libyaml-dev

## Utilities and Python
RUN apt-get install -y make wget tar git python3-pip python3-dev python3-software-properties

## Clean apt-get
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

## Install libsodium
RUN wget https://github.com/jedisct1/libsodium/releases/download/1.0.0/libsodium-1.0.0.tar.gz && \
  tar xzvf libsodium-1.0.0.tar.gz && \
  cd libsodium-1.0.0 && \
  ./configure && \
  make && make check && sudo make install && \
  cd .. && rm -rf libsodium-1.0.0 && \
  sudo ldconfig

# App User
RUN useradd -ms /bin/bash app
RUN adduser app sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN chmod 4755 /usr/bin/sudo
ENV HOME /home/app

EXPOSE 8000

# Don't run application as root
USER app

WORKDIR /usr/src/app/
ADD requirements.txt /usr/src/app/requirements.txt
RUN sudo pip3 install -r requirements.txt

ADD . /usr/src/app/
RUN sudo chown -R app /usr/src/app/
