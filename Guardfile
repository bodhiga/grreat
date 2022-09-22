#!/usr/bin/env python3

from livereload import Server, shell

server = Server()
server.watch('./*/*.py', shell('python3 quant.py'))
server.serve()
