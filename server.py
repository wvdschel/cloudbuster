import http.server
import socketserver
import json
from src.cf import scrape_cf_turnstile

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'healthy'}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/token':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                request_data = json.loads(post_data.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': 'malformed request body'}
                self.wfile.write(json.dumps(response).encode())
            
            # Get the link from request data
            link = request_data.get('link')
            if not link:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': 'Link parameter is required'}
                self.wfile.write(json.dumps(response).encode())
                return
            
            try:
                # Scrape Cloudflare token and cookies
                result = scrape_cf_turnstile(link, request_data.get('proxy'))
                
                # Extract cookies and token from the result
                cookies = result.get('cookies', {})
                local_storage = result.get('local_storage', {})
                token = local_storage.get('captured_cf_token')
                
                if not token:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'error': 'Failed to capture CF token'}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Return both cookies and token
                response = {
                    'token': token,
                    'cookies': cookies
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'error': f'Error scraping CF token: {str(e)}'}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()


PORT = 8000
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Server running at port {PORT}")
    httpd.serve_forever()
