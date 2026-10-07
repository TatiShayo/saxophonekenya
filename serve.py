from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
import sys

class CustomHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def run(port=8080):
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)
    server_address = ('0.0.0.0', port)
    
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(server_address, CustomHandler)
    print(f"Server started at http://localhost:{port} (http://127.0.0.1:{port})", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)
