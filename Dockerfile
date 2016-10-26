FROM debian:latest

MAINTAINER Jonathan Gordon <jgordon@isi.edu>

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8


# Install system dependencies.

ARG DEBIAN_FRONTEND=noninteractive

RUN echo deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main \
    | tee /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886

RUN apt-get update -q -y --fix-missing
RUN apt-get upgrade -q -y --fix-missing

RUN apt-get install -q -y --fix-missing wget bzip2 git g++ make

RUN echo debconf shared/accepted-oracle-license-v1-1 select true | \
    debconf-set-selections && \
    apt-get install -q -y --fix-missing oracle-java8-installer \
        oracle-java8-set-default maven

RUN apt-get clean -q

RUN rm -rf /var/cache/oracle-jdk8-installer


# Install Miniconda.

RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
         -O ~/miniconda.sh --quiet && \
    bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

ENV PATH /opt/conda/bin:$PATH

RUN conda update -y conda


# Install external tools.

RUN mkdir -p /t/ext

WORKDIR /t/ext


# Install Mallet.

RUN wget http://mallet.cs.umass.edu/dist/mallet-2.0.8RC3.tar.gz --quiet && \
    tar xvf mallet-2.0.8RC3.tar.gz && \
    mv mallet-2.0.8RC3 mallet && \
    rm mallet-2.0.8RC3.tar.gz


# Install Infomap.

RUN wget http://www.mapequation.org/downloads/Infomap.zip --quiet && \
    unzip Infomap.zip -d infomap && \
    rm Infomap.zip && \
    cd infomap && \
    make


# Check out and compile TechKnAcq Core.

RUN git clone https://github.com/ISI-TechknAcq/techknacq-core.git && \
    cd techknacq-core && \
    mvn package && \
    cd target && \
    ln -s *jar techknacq-core.jar


# Add TechKnAcq code.

ADD lib /t/lib
ADD build-corpus /t
ADD concept-graph /t
ADD reading-list /t
ADD server /t


# Run TechKnAcq.

WORKDIR /t
