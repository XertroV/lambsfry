lambsfry
========

Lightweight url minifyer using flask and redis

# Dependancies

* Flask
* pycrypto
* redis-py

# Config

There are only 4 config options:

* logfilename - self explanitory
* dbnum - number of the db to use in redis
* dbPre - arbitrary string to attempt to avoid colisions if you do accidentally use a common database
* siteUrl - used to generate links to print

Just edit them in the top few lines of `lambsfry.py`
