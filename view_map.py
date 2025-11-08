import http.server
import socketserver
import webbrowser
import os

PORT = 8000
# The path to the map relative to the project root
MAP_FILE_PATH = "output/comparison/results_map.html"

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = MAP_FILE_PATH
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Create the server
Handler = MyHttpRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

# The URL to open
url = f"http://localhost:{PORT}"

print("="*80)
print(f"Starting local web server...")
print(f"If your browser doesn't open automatically, please go to:")
print(url)
print("Press Ctrl+C to stop the server.")
print("="*80)

# Open the web browser
webbrowser.open(url)

# Start the server
httpd.serve_forever()
