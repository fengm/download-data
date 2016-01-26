'''
File: download_data.py
Author: Min Feng
Version: 0.1
Create: 2016-01-26 14:58:42
Description: download data in a list using multi-task
'''
import logging

def download(url, pos, lock):
	import run_commands
	try:
		run_commands.run(['wget', '-c', url], False, cwd=pos)
	except Exception:
		logging.error('failed (%s)' % url)
		with lock:
			with open('failed_scenes.txt', 'a') as _fo:
				_fo.write('%s\n' % url)

def main():
	_opts = _init_env()

	import os
	_d_out = _opts.output
	os.path.exists(_d_out) or os.makedirs(_d_out)

	_ps = []
	import gzip
	with gzip.open(_opts.input, 'r') if _opts.input.endswith('.gz') else open(_opts.input, 'r') as _fi:
		for _l in _fi:
			_l = _l.strip()
			if not _l:
				continue

			_f_out = os.path.join(_d_out, _l.split('/')[-1])
			if os.path.exists(_f_out) and _opts.skip:
				logging.info('skip existing file %s' % _l)
				continue

			_ps.append((_l.strip(), _d_out))

	import multi_task
	multi_task.run(download, multi_task.load(_ps, _opts), _opts, (multi_task.create_lock(), ))

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config')
	_p.add_argument('--temp', dest='temp')

	_p.add_argument('-i', '--input', dest='input', required=True)
	_p.add_argument('-s', '--skip', dest='skip', default=False, action='store_true')
	_p.add_argument('-o', '--output', dest='output', required=True)

	import multi_task
	multi_task.add_task_opts(_p)

	return _p.parse_args()

def _init_env():
	import os, sys

	_dirs = ['lib', 'libs']
	_d_ins = [os.path.join(sys.path[0], _dirs) for _d in _dirs if \
			os.path.exists(os.path.join(sys.path[0], _d))]
	sys.path = [sys.path[0]] + _d_ins + sys.path[1:]

	_opts = _usage()

	import logging_util
	logging_util.init(_opts.logging)

	import config
	config.load(_opts.config)

	import file_unzip as fz
	fz.clean(fz.default_dir(_opts.temp))

	return _opts

if __name__ == '__main__':
	main()

