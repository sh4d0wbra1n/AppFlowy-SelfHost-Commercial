#!/usr/bin/env python3
"""Patch a clean clone/fork of AppFlowy-SelfHost-Commercial for HomeLab Portainer.
Run locally against checked-out repository, then commit/push to private fork.
"""
from pathlib import Path
import re, sys
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
compose=root/'docker-compose.yml'
env=root/'deploy.env'
assert compose.is_file() and env.is_file(), 'Run from official repository root'
s=compose.read_text()
old='''    ports:
      - ${NGINX_PORT:-80}:80   # Disable this if you are using TLS
      - ${NGINX_TLS_PORT:-443}:443'''
new='''    ports: [] # NPM reaches nginx over npm-nw; no host ports
    networks:
      default:
      npm-nw:
        aliases:
          - appflowy-test-nginx'''
assert s.count(old)==1, 'Official nginx stanza changed; inspect and update patch'
s=s.replace(old,new,1)
# Named app volumes are intentionally kept; database, minio and keyword index stay fully isolated within stack.
s += '''\nnetworks:\n  npm-nw:\n    external: true\n'''
compose.write_text(s)
# Portainer Git stack must use Portainer Environment variables to interpolate Compose fields.
# deploy.env is a template to copy into Portainer's stack environment variables or a secured .env.
print('Patched docker-compose.yml. Add environment variables from deploy.env in Portainer (with secrets replaced).')
print('Do NOT run this twice. Set FQDN/SCHEME/WS_SCHEME and credentials before deployment.')
