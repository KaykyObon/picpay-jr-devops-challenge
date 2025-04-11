#!/usr/bin/env python3
import http.server
import socketserver
import json
import redis  # type: ignore

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self._send_cors_headers()
        self.end_headers()

        if self.path == '/health':
            self.wfile.write(b'"up"')
        else:
            self.wfile.write(b'{"message": "Unknown endpoint"}')

    def do_POST(self):
        self.send_response(201)
        self.send_header("Content-type", "application/json")
        self._send_cors_headers()
        self.end_headers()

        if self.path == '/write':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                redishost = "redis"
                redisclient = redis.Redis(host=redishost)
                redisclient.set("SHAREDKEY", post_data.decode('utf-8'))
                self.wfile.write(b'{"message": "Data saved"}')
            except redis.RedisError as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))


handler_object = RequestHandler
socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(("", 8081), handler_object)
server.serve_forever()