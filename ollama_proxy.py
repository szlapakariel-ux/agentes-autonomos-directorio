#!/usr/bin/env python3
"""
Proxy local para Ollama en Windows
Redirecciona localhost:11434 → 192.168.0.62:11434
Corre en segundo plano y permite acceso local sin proxy
"""

import http.server
import socketserver
import urllib.request
import urllib.error
from urllib.parse import urlparse
import sys

WINDOWS_OLLAMA_URL = "http://192.168.0.62:11434"
LOCAL_PORT = 11434

class OllamaProxyHandler(http.server.BaseHTTPRequestHandler):
    """Handler que redirecciona requests a Windows Ollama"""

    def do_GET(self):
        self._proxy_request("GET")

    def do_POST(self):
        self._proxy_request("POST")

    def do_PUT(self):
        self._proxy_request("PUT")

    def do_DELETE(self):
        self._proxy_request("DELETE")

    def _proxy_request(self, method):
        """Proxy la request al Ollama de Windows"""
        try:
            # Construir URL en Windows (path incluye query string)
            target_url = f"{WINDOWS_OLLAMA_URL}{self.path}"

            # Preparar headers
            headers = {k: v for k, v in self.headers.items()
                      if k.lower() not in ['host', 'connection']}

            # Obtener body si existe
            body = None
            if method in ["POST", "PUT"]:
                content_length = self.headers.get('Content-Length', 0)
                if content_length:
                    body = self.rfile.read(int(content_length))

            # Hacer request
            req = urllib.request.Request(
                target_url,
                data=body,
                headers=headers,
                method=method
            )

            # Recibir response
            with urllib.request.urlopen(req, timeout=60) as response:
                status = response.status
                resp_headers = dict(response.headers)
                resp_body = response.read()

            # Enviar response al cliente
            self.send_response(status)
            for header, value in resp_headers.items():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(resp_body)

        except urllib.error.URLError as e:
            self.send_response(503)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            error_msg = f"❌ No se puede conectar a Ollama en {WINDOWS_OLLAMA_URL}: {str(e)}\n"
            self.wfile.write(error_msg.encode())
            print(f"[ERROR] {error_msg}")

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            error_msg = f"❌ Error en proxy: {str(e)}\n"
            self.wfile.write(error_msg.encode())
            print(f"[ERROR] {error_msg}")

    def log_message(self, format, *args):
        """Customizar logs"""
        print(f"[PROXY] {self.client_address[0]} - {format % args}")


def main():
    """Inicia el proxy"""
    handler = OllamaProxyHandler
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("127.0.0.1", LOCAL_PORT), handler) as httpd:
            print(f"✅ Proxy iniciado:")
            print(f"   Escuchando en:  http://127.0.0.1:{LOCAL_PORT}")
            print(f"   Redirigiendo a: {WINDOWS_OLLAMA_URL}")
            print(f"\nUso en orquestador:")
            print(f'   ollama_url = "http://127.0.0.1:{LOCAL_PORT}"')
            print(f"\nPresiona Ctrl+C para detener\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Proxy detenido")
        sys.exit(0)
    except OSError as e:
        print(f"❌ Error al iniciar proxy: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
