#!/bin/bash
source musicenv/bin/activate
gunicorn --config configunicorn.py --timeout 12000  app:app