FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:5dfeffe524374adf60c0100d6705643cf250c55247d5e86d99d3168583393ad5

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
