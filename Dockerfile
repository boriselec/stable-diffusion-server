FROM ghcr.io/boriselec/stable-diffusion-docker:init

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
