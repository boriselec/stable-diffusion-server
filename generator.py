#!/usr/bin/env python
from types import SimpleNamespace
import stablediffusion


def generate_loop(job_queue, curr_rq, startup_args):
    args = SimpleNamespace(device=startup_args.device,
                           model=startup_args.model,
                           half=startup_args.half,
                           height=startup_args.height,
                           width=startup_args.width,
                           steps=startup_args.steps,
                           token='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',
                           skip=True,
                           seed=519762248,
                           scale=7.5,
                           strength=0.75,
                           image=None,
                           image_scale=None,
                           negative_prompt=None,
                           scheduler=None,
                           xformers_memory_efficient_attention=False,
                           attention_slicing=False,
                           mask=None)
    while True:
        job = job_queue.get()
        curr_rq.value = job.rq
        args.prompt = job.art_desc
        pipeline = stablediffusion.stable_diffusion_pipeline(args)
        stablediffusion.stable_diffusion_inference(pipeline, job.rq)
