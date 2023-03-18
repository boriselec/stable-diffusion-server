FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:f9f81f8f4c0205f5fac0f2240c39bc86a8f5ffd56cf7ad6fc4a4dac0d62481c0

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
