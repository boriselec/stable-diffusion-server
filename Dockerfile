FROM ghcr.io/fboulnois/stable-diffusion-docker:1.31.0

COPY server.py /usr/local/bin
COPY stablediffusion.py /usr/local/bin
COPY generator.py /usr/local/bin

EXPOSE 8080

ENTRYPOINT [ "python3", "/usr/local/bin/server.py" ]
