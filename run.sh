#!/bin/bash
source musicenv/bin/activate
gunicorn --worker-class=gevent --config configunicorn.py --timeout 12000 app:app