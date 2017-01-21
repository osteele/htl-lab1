# Set the base image.
# Use Ubuntu for compatibility with student build environments.
FROM ubuntu
MAINTAINER Oliver Steele

# Usage:
#    docker build -t htl-lab1 .
#    docker run -v .:/app -p 5000:5000 htl-lab1
#
# To attach to a running process:
#    docker ps  # replace 97b04c634241 by the container id
#    docker exec -i -t 97b04c634241 /bin/bash

ARG DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip python3-dev build-essential
RUN apt-get -y install curl  # for debugging
RUN apt-get -y install python3-numpy
RUN apt-get -y install python3-pandas

# For lab1, we aren't using a requirements.txt file.
# Later in the semester, replace this by:
#   RUN mkdir -p /tmp/python-requirements
#   COPY requirements.txt /tmp/python-requirements/requirements.txt
#   RUN pip3 install -r /tmp/python-requirements/requirements.txt

# RUN pip3 install pandas  # runs, but with distracting error messages
RUN pip3 install Flask

# Create a n application source directory.
# The caller must bind this directory to a volue that contains
# `server.py`, via the `-v` option to `docker run` or the
# `volumes` configuration in a `docker-compose` file.
RUN mkdir -p /app
WORKDIR /app

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8
ENV FLASK_APP server.py
ENV FLASK_DEBUG 1

# Use a private port mapping, so that multiple instances
# can run concurrently on the same host.
EXPOSE 5000

ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]

# Clear the listing to save space.
# Do this last so that modifying the apt-get list above doesn't
# require downloading everything from the internet again.
# RUN rm -rf /var/lib/apt/lists/*

# (Actually, we're skipping this in development so that we
# can more easily experiment when signing into a machine.)
