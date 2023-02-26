#!/usr/bin/env python
import argparse, datetime, inspect, os, warnings
import numpy as np
import torch
from PIL import Image
from diffusers import (
    OnnxStableDiffusionPipeline,
    OnnxStableDiffusionInpaintPipeline,
    OnnxStableDiffusionImg2ImgPipeline,
    StableDiffusionDepth2ImgPipeline,
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline,
    StableDiffusionInstructPix2PixPipeline,
    StableDiffusionUpscalePipeline,
    schedulers,
)


def iso_date_time():
    return datetime.datetime.now().isoformat()


def load_image(path):
    image = Image.open(os.path.join("input", path)).convert("RGB")
    print(f"loaded image from {path}:", iso_date_time(), flush=True)
    return image


def remove_unused_args(p):
    params = inspect.signature(p.pipeline).parameters.keys()
    args = {
        "prompt": p.prompt,
        "negative_prompt": p.negative_prompt,
        "image": p.image,
        "mask_image": p.mask,
        "height": p.height,
        "width": p.width,
        "num_inference_steps": p.steps,
        "guidance_scale": p.scale,
        "image_guidance_scale": p.image_scale,
        "strength": p.strength,
        "generator": p.generator,
    }
    return {p: args[p] for p in params if p in args}


def stable_diffusion_pipeline(p):
    p.dtype = torch.float16 if p.half else torch.float32

    if p.device == "cpu":
        p.diffuser = OnnxStableDiffusionPipeline
        p.revision = "onnx"
    else:
        p.diffuser = StableDiffusionPipeline
        p.revision = "fp16" if p.half else "main"

    models = argparse.Namespace(
        **{
            "depth2img": ["stabilityai/stable-diffusion-2-depth"],
            "pix2pix": ["timbrooks/instruct-pix2pix"],
            "upscalers": ["stabilityai/stable-diffusion-x4-upscaler"],
        }
    )
    if p.image is not None:
        if p.revision == "onnx":
            p.diffuser = OnnxStableDiffusionImg2ImgPipeline
        elif p.model in models.depth2img:
            p.diffuser = StableDiffusionDepth2ImgPipeline
        elif p.model in models.pix2pix:
            p.diffuser = StableDiffusionInstructPix2PixPipeline
        elif p.model in models.upscalers:
            p.diffuser = StableDiffusionUpscalePipeline
        else:
            p.diffuser = StableDiffusionImg2ImgPipeline
        p.image = load_image(p.image)

    if p.mask is not None:
        if p.revision == "onnx":
            p.diffuser = OnnxStableDiffusionInpaintPipeline
        else:
            p.diffuser = StableDiffusionInpaintPipeline
        p.mask = load_image(p.mask)

    if p.token is None:
        with open("token.txt") as f:
            p.token = f.read().replace("\n", "")

    if p.seed == 0:
        p.seed = torch.random.seed()

    if p.revision == "onnx":
        p.seed = p.seed >> 32 if p.seed > 2**32 - 1 else p.seed
        p.generator = np.random.RandomState(p.seed)
    else:
        p.generator = torch.Generator(device=p.device).manual_seed(p.seed)

    print("load pipeline start:", iso_date_time(), flush=True)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning)
        pipeline = p.diffuser.from_pretrained(
            p.model,
            torch_dtype=p.dtype,
            revision=p.revision,
            use_auth_token=p.token,
        ).to(p.device)

    if p.scheduler is not None:
        scheduler = getattr(schedulers, p.scheduler)
        pipeline.scheduler = scheduler.from_config(pipeline.scheduler.config)

    if p.skip:
        pipeline.safety_checker = None

    if p.attention_slicing:
        pipeline.enable_attention_slicing()

    if p.xformers_memory_efficient_attention:
        pipeline.enable_xformers_memory_efficient_attention()

    p.pipeline = pipeline

    print("loaded models after:", iso_date_time(), flush=True)

    return p


def stable_diffusion_inference(p):
    result = p.pipeline(**remove_unused_args(p))
    img = result.images[0]
    img_path = os.path.join("output", "current.png")
    img.save(img_path)

    print("completed pipeline:", iso_date_time(), flush=True)

