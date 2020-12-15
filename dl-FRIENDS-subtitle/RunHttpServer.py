import http.server
import os
import socketserver

import background as bg

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

os.chdir(os.path.join(os.path.dirname(__file__), "templates"))


with bg.BackgroundTask() as b:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
