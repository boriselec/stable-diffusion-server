FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  git \
  && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/Stability-AI/stablediffusion /home/stablediffusion \
  && cd /home/stablediffusion \
  && git checkout d55bcd4d31d0316fcbdf552f2fd2628fdc812500
