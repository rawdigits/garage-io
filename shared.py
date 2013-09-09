import redis
import time
from config import *

def wait_for_redis():
  r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
  while True:
    try:
      r.get("test")
      break
    except:
      time.sleep(1)
      print "Waiting for redis..."
