#!/bin/sh
env XDG_SESSION_TYPE=x11 QT_QPA_PLATFORM=xcb ./run.py "$@"
