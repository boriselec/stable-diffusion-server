FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:bcf1a6563781e22669807de4e369c21810bc29ba8300960ca415dc8c10b42167

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
