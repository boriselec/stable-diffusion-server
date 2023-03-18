FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:486299f43c6180af69edb7b5778ffac823c4f1045a0afb822922e8beb83b0c61

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
