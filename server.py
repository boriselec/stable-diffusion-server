#!/usr/bin/env python
import importlib
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from types import SimpleNamespace

stable_diffusion = importlib.import_module("docker-entrypoint")

hostName = "0.0.0.0"
serverPort = 8081


class GenerationServer(BaseHTTPRequestHandler):
    lock = threading.Lock()

    def do_POST(self):
        if self.path.startswith('/generate'):
            if self.lock.acquire(blocking=False):
                try:
                    content_length = int(self.headers['Content-Length'])
                    data = self.rfile.read(content_length).decode('utf-8')

                    print("inference..", flush=True)
                    args = SimpleNamespace(
                        prompt=data,
                        height=startup_args.height,
                        width=startup_args.width,
                        strength=startup_args.strength,
                        steps=startup_args.steps,
                        samples=startup_args.samples,
                        scale=startup_args.scale,
                        negative_prompt=None,
                        image=None,
                        mask=None,
                        image_scale=None,
                        pipeline=pipeline,
                        iters=startup_args.iters,
                        seed=startup_args.seed,
                        generator=generator)
                    img_paths = stable_diffusion.stable_diffusion_inference(args)
                    print("inference done", flush=True)

                    f = open(img_paths[0], 'rb')
                    self.send_response(200)
                    self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()

                    for img_path in img_paths:
                        os.remove(img_path)

                except RuntimeError:
                    logging.exception("Error processing request")
                    self.send_error(500)
                finally:
                    self.lock.release()
            else:
                self.send_error(503, 'Busy')

        else:
            self.send_error(404, 'Not found')


if __name__ == "__main__":
    startup_args = stable_diffusion.parse_args()
    p = stable_diffusion.stable_diffusion_pipeline(startup_args)
    pipeline = p.pipeline
    generator = p.generator

    webServer = HTTPServer((hostName, serverPort), GenerationServer)
    print("Server started http://%s:%s\n" % (hostName, serverPort), flush=True)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.", flush=True)
