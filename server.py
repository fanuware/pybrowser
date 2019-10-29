#!/usr/bin/env python3

import sys

def serve_forever(port, cgi_directories):
    if sys.version_info < (3, 0):
        import CGIHTTPServer
        import BaseHTTPServer

        class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
            cgi_directories = CGI_DIRECTORIES

        server = BaseHTTPServer.HTTPServer(('', port), Handler)
    else:
        from http.server import CGIHTTPRequestHandler, HTTPServer

        handler = CGIHTTPRequestHandler
        handler.cgi_directories = CGI_DIRECTORIES

        server = HTTPServer(('localhost', port), handler)

    print ('Server started on port', port)
    server.serve_forever()


if __name__ == '__main__':
    PORT = 8440 if len(sys.argv) <= 1 else int(sys.argv[1])
    CGI_DIRECTORIES = ['/cgi-bin']
    serve_forever(PORT, CGI_DIRECTORIES)
