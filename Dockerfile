FROM ghcr.io/boriselec/stable-diffusion-docker:main_fork

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
