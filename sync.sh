#!/bin/bash
rsync -avr --delete-after --exclude="musicenv" --exclude=".git" --exclude=".idea" --exclude="musico.sqlite3" --exclude="__pycache__" --exclude="app/__pychache__" --exclude="app/static/musique" --exclude="app/static/user_data/" . manu@192.168.1.128:~/musico/
