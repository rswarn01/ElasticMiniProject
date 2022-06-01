# REFERENCE - https://github.com/twright-msft/mssql-node-docker-demo-app
FROM mcr.microsoft.com/mssql/server:2019-latest

# Switch to root user for access to apt-get install
USER root

# Install dos2unix
RUN apt-get -y update  && \
    apt-get install -y dos2unix

# Create app directory to load startup scripts
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Bundle app source
COPY . /usr/src/app

# convert the file from DOS(Windows) format to UNIX format
RUN dos2unix *

# Grant permissions for the setup_databse script to be executable
RUN chmod +x /usr/src/app/create_databse.sh

ENTRYPOINT /bin/bash ./entrypoint.sh