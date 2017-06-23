#!/usr/bin/env python


from test_lock_file import Config

config = Config.read()

print(config['key'])
