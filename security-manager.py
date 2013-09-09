#!/usr/bin/python

from bottle import route, run
import redis

from config import *

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

@route('/mode/<mode>')
def mode(mode):
  r.set('security-mode',mode)
  return "Mode changed!"

@route('/status')
def status():
  return "<h1>%s %s</h1>" % (r.get('security-status'), r.get('security-mode'))

@route('/command/<command>')
def command(command):
  r.set('command',command)

run(host='0.0.0.0', port=8080)
