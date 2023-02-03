FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
  git \
  python-is-python3 \
  wget \
  && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/Stability-AI/stablediffusion /home/stablediffusion \
  && cd /home/stablediffusion \
  && git checkout d55bcd4d31d0316fcbdf552f2fd2628fdc812500
RUN wget -P /home/stablediffusion-model/ \
  https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/36a01dc742066de2e8c91e7cf0b8f6b53ef53da1/v2-1_768-ema-pruned.ckpt
