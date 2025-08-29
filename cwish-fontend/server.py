#!/usr/bin/env python3
"""
Simple HTTP server with URL rewriting for clean URLs
"""
import http.server
import socketserver
import os
import urllib.parse
from pathlib import Path

class URLRewriteHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # URL rewriting rules
        url_mappings = {
            '/': '/home.html',
            '/home': '/home.html',
            '/nectar': '/nectar.html',
            '/contact': '/contact.html',
            '/login': '/login.html',
            '/signup': '/signup.html',
            '/account': '/my-account.html',
            '/cart': '/cart.html',
            '/test-cart': '/test-cart.html'
        }
        
        # Check if we need to rewrite the URL
        if path in url_mappings:
            self.path = url_mappings[path]
        elif not path.endswith('.html') and not path.endswith('/') and '.' not in path:
            # If no extension and not a directory, try adding .html
            html_path = path + '.html'
            if os.path.exists(html_path[1:]):  # Remove leading slash
                self.path = html_path
        
        # Call the parent class method
        super().do_GET()

def run_server(port=8080):
    """Run the HTTP server with URL rewriting"""
    handler = URLRewriteHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server running at http://localhost:{port}")
        print("Clean URLs available:")
        print(f"  http://localhost:{port}/")
        print(f"  http://localhost:{port}/home")
        print(f"  http://localhost:{port}/nectar")
        print(f"  http://localhost:{port}/contact")
        print(f"  http://localhost:{port}/cart")
        print(f"  http://localhost:{port}/test-cart")
        print("\nPress Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()
