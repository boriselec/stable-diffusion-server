#!/usr/bin/env python
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer

import generator

hostName = "0.0.0.0"
serverPort = 8081


class GenerationServer(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.startswith('/generate'):
            self.send_response(200)

            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode('utf-8')

            generator.generate(data, startup_args)

            f = open('output/current.png', 'rb')
            self.send_header("Content-type", "image/png")
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

        else:
            self.send_error(404, 'Not found')


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
        default="dreamlike-art/dreamlike-diffusion-1.0",
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
    webServer = HTTPServer((hostName, serverPort), GenerationServer)
    print("Server started http://%s:%s\n" % (hostName, serverPort), flush=True)

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.", flush=True)
