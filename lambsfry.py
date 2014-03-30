#!/usr/bin/python

'''Public domain or something. Do what you want.
- Max Kaye'''
''' Minifier written with Flask and redis '''
''' LaMbsFRy: Light Minifier Flask Redis '''

# config
logfilename = 'lmfr.log'
dbnum = 1
dbPre = 'lmfr'
siteUrl = 'http://127.0.0.1:5000/'

# import and init
from flask import Flask
from flask import request, render_template, redirect
app = Flask(__name__)

import logging
log_handler = logging.FileHandler(logfilename)
log_handler.setLevel(logging.WARNING)
app.logger.addHandler(log_handler)

from Crypto.Hash import SHA256
from binascii import hexlify

# helpers
def sha256Hash(plaintext):
	h = SHA256.new()
	h.update(plaintext)
	return h.digest()
	
## from python-bitcoinlib
b58_digits = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58encode(b):
    n = int('0x0' + hexlify(b).decode('utf8'), 16)
    res = []
    while n > 0:
        n, r = divmod (n, 58)
        res.append(b58_digits[r])
    res = ''.join(res[::-1])
    czero = b'\x00'
    pad = 0
    for c in b:
        if c == czero: pad += 1
        else: break
    return b58_digits[0] * pad + res
	
# database
class Database:
	def __init__(self):
		import redis
		self.r = redis.StrictRedis(host='localhost', port=6379, db=dbnum)
		self.dbPre = dbPre
	def exists(self,toTest):
		return self.r.exists('%s:%s' % (self.dbPre,toTest))
	def set(self,toSet,value):
		return self.r.set('%s:%s' % (self.dbPre,toSet),value)
	def get(self,toGet):
		return self.r.get('%s:%s' % (self.dbPre,toGet))
	def rpush(self,toPush, value):
		return self.r.rpush('%s:%s' % (self.dbPre,toPush), value)
	def addSite(self, url):
		urlHash = b58encode(sha256Hash(url))
		if self.exists('urlHashToFB:%s' % urlHash):
			return self.get('urlHashToFB:%s' % urlHash)
		for fbLen in range(1,len(urlHash)+1):
			if not self.exists('fbToUrlHash:%s' % urlHash[:fbLen]):
				fb = urlHash[:fbLen]
				self.set('urlHashToFB:%s' % urlHash, fb)
				self.set('urlHashToUrl:%s' % urlHash, url)
				self.set('fbToUrlHash:%s' % fb, urlHash)
				self.set('fbToUrl:%s' % fb, url)
				self.rpush('listOfHashs', urlHash)
				return siteUrl + fb
		return 'Error, no spare firstbits found :( -- that should not happen...'		
	def checkFb(self, fb):
		return self.get('fbToUrl:%s' % fb) if self.exists('fbToUrl:%s' % fb) else False

# routes
@app.route("/<path:fb>")
def lookup(fb):
	url = db.checkFb(fb)
	return redirect(url) if url != False else '%s firstbits not found' % fb

@app.route("/",methods=["GET","POST"])
def main():
	if request.method == "POST":
		url = request.form['urlin']
		link = db.addSite('http://' + url)
		return render_template('result.html',url=url,link=link)
	return render_template('index.html')

if __name__ == "__main__":
	db = Database()
	app.run()
