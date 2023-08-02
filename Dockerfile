FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:df1c447fdae1263762239e569ca990c4c4f0cd2b5b509d8abaa5cbbb7bb43c45

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
