FROM ghcr.io/boriselec/stable-diffusion-docker@sha256:ecadb18d76665e0f35018ae79f16a2e4ac59ef7f6b4235a7ffda4c88487df4f9

COPY server.py /usr/local/bin

EXPOSE 8081

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
