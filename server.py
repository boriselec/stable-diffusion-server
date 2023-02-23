#!/usr/bin/env python
import argparse
import hashlib
import threading
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from queue import Queue
from types import SimpleNamespace

import generator

hostName = "0.0.0.0"
serverPort = 8080


class GenerationServer(BaseHTTPRequestHandler):
    def __init__(self, job_queue, curr_rq, *args, **kwargs):
        self.job_queue = job_queue
        self.curr_rq = curr_rq
        super().__init__(*args, **kwargs)

    def do_POST(self):
        if self.path.startswith('/generate'):
            self.send_response(200)

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = post_data.split(';')

            m = hashlib.sha256()
            m.update(''.join(data).encode())

            rq_id = m.hexdigest()
            art_desc = data[0]
            thing_desc = data[1]

            print("rq_id: %s\nart_desc: %s\nthing_desc: %s" % (rq_id, art_desc, thing_desc), flush=True)

            try:
                self.send_image(rq_id)
            except OSError:
                queue_pos = self.queue_pos(rq_id)
                if queue_pos is None:
                    job = SimpleNamespace(rq=rq_id, art_desc=art_desc, thing_desc=thing_desc)
                    self.job_queue.put(job)
                    queue_pos = self.job_queue.qsize()
                self.send_in_progress(queue_pos)

        else:
            self.send_error(404, 'Not found')

    def queue_pos(self, rq_id):
        if self.curr_rq.value == rq_id:
            return 0
        else:
            for idx, job in enumerate(self.job_queue.queue):
                if job.rq == rq_id:
                    return idx + 1
            return None

    def send_image(self, rq_id):
        f = open('output/%s.png' % rq_id, 'rb')
        self.send_header("Content-type", "image/png")
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    def send_in_progress(self, queue_pos):
        self.send_header("Content-type", "text")
        self.end_headers()
        self.wfile.write(bytes('Queue position: %d' % queue_pos, "utf-8"))


def parse_args():
    global startup_args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--device",
        type=str,
        nargs="?",
        default="cuda",
        help="The cpu or cuda device to use to render images",
    )
    parser.add_argument(
        "--half",
        type=bool,
        nargs="?",
        const=True,
        default=False,
        help="Use float16 (half-sized) tensors instead of float32",
    )
    parser.add_argument(
        "--model",
        type=str,
        nargs="?",
        default="CompVis/stable-diffusion-v1-4",
        help="The model used to render images",
    )
    parser.add_argument(
        "--steps", type=int, nargs="?", default=50, help="Number of sampling steps"
    )
    parser.add_argument(
        "--height", type=int, nargs="?", default=512, help="Image height in pixels"
    )
    parser.add_argument(
        "--width", type=int, nargs="?", default=512, help="Image width in pixels"
    )
    return parser.parse_args()


if __name__ == "__main__":
    startup_args = parse_args()

    queue = Queue()
    curr_rq_holder = SimpleNamespace(value=None)

    handler = partial(GenerationServer, queue, curr_rq_holder)
    webServer = HTTPServer((hostName, serverPort), handler)
    print("Server started http://%s:%s\n" % (hostName, serverPort), flush=True)

    threading.Thread(target=generator.generate_loop, args=[queue, curr_rq_holder, startup_args]).start()

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.", flush=True)
