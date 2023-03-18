FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:dd08f3388c8150c7512918b68d173910f133570cc75db829a3cf3cd3c5d1cdc1

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
