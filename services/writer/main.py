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
            print(f"Recebido POST data: {post_data.decode('utf-8')}")  # Log para depuração
            try:
                redishost = "redis"  # Nome do serviço no docker-compose.yaml
                redisclient = redis.Redis(host=redishost, port=6379)

                # Testa a conexão com o Redis
                print("Tentando conectar ao Redis...")
                redisclient.ping()
                print("Conexão com o Redis bem-sucedida!")

                # Salva os dados no Redis
                print("Tentando salvar os dados no Redis...")
                redisclient.set("SHAREDKEY", post_data.decode('utf-8'))
                print("Dados salvos no Redis com sucesso!")
                self.wfile.write(b'{"message": "Data saved"}')
            except redis.ConnectionError as e:
                print(f"Erro de conexão com o Redis: {e}")
                self.wfile.write(json.dumps({"error": "Redis connection error"}).encode("utf-8"))
            except redis.RedisError as e:
                print(f"Erro ao salvar no Redis: {e}")
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            except Exception as e:
                print(f"Erro inesperado: {e}")
                self.wfile.write(json.dumps({"error": "Unexpected error"}).encode("utf-8"))


handler_object = RequestHandler
socketserver.TCPServer.allow_reuse_address = True
server = socketserver.TCPServer(("", 8081), handler_object)
server.serve_forever()