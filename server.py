#!/usr/bin/env python
import copy
import importlib
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

generator = importlib.import_module("docker-entrypoint")

hostName = "0.0.0.0"
serverPort = 8081


class GenerationServer(BaseHTTPRequestHandler):
    lock = threading.Lock()

    def do_POST(self):
        if self.path.startswith('/generate'):
            free = self.lock.acquire(blocking=False)
            if not free:
                self.send_error(503, 'Busy')
            try:
                self.send_response(200)

                content_length = int(self.headers['Content-Length'])
                data = self.rfile.read(content_length).decode('utf-8')
                args = copy.deepcopy(startup_args)
                args.prompt = data

                pipeline = generator.stable_diffusion_pipeline(args)
                img_paths = generator.stable_diffusion_inference(pipeline)

                f = open(img_paths[0], 'rb')
                self.send_header("Content-type", "image/png")
                self.end_headers()
                self.wfile.write(f.read())
                f.close()

                for img_path in img_paths:
                    os.remove(img_path)
            finally:
                self.lock.release()

        else:
            self.send_error(404, 'Not found')


if __name__ == "__main__":
    startup_args = generator.parse_args()
    webServer = HTTPServer((hostName, serverPort), GenerationServer)
    print("Server started http://%s:%s\n" % (hostName, serverPort), flush=True)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.", flush=True)
