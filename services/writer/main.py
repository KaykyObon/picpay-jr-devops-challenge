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
        if self.path != '/write':
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Unknown endpoint"}')
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = post_data.decode('utf-8')

            # Optional: print incoming data
            print(f"Received data: {payload}")

            # Connect to Redis and set key
            redishost = "redis"
            redisclient = redis.Redis(host=redishost, port=6379, decode_responses=True)
            redisclient.set("SHAREDKEY", payload)

            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"message": "Data saved"}')

        except redis.RedisError as e:
            self.send_response(500)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        except Exception as e:
            self.send_response(400)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

# Run the server
handler_object = RequestHandler
socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(("", 8081), handler_object)
print("Writer service started on port 8081...")
server.serve_forever()