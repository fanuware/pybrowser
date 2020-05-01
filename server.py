#!/usr/bin/env python3

import sys
import argparse

def serve_forever(host, port, cgi_directories):
    if sys.version_info < (3, 0):
        import CGIHTTPServer
        import BaseHTTPServer

        class Handler(CGIHTTPServer.CGIHTTPRequestHandler):
            cgi_directories = CGI_DIRECTORIES

        server = BaseHTTPServer.HTTPServer((host, port), Handler)
    else:
        from http.server import CGIHTTPRequestHandler, HTTPServer

        handler = CGIHTTPRequestHandler
        handler.cgi_directories = CGI_DIRECTORIES

        server = HTTPServer((host, port), handler)

    print ('Server started ({}, {})'.format(host, port))
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run CGI Server.')
    parser.add_argument('--host', default='localhost',
                        help='Server host address')
    parser.add_argument('--port', type=int, default=8440,
                        help='Server port')
    args = parser.parse_args()

    CGI_DIRECTORIES = ['/cgi-bin']
    serve_forever(args.host, args.port, CGI_DIRECTORIES)
