'''
File: download_modis_list.py
Author: Min Feng
Version: 0.1
Create: 2016-01-26 14:58:55
Description: download MODIS data list
'''

def _load_list(f):
	print 'loading list', f
	import os

	_ds = {}
	with open(f) as _fi:
		for _l in _fi:
			_d, _f = os.path.split(_l.strip())
			_d += '/'
			if _d not in _ds:
				_ds[_d] = []
			_ds[_d].append(_l.strip())

	print 'loaded', len(_ds.keys()), 'folders'
	return _ds

def download_folder_http(url, ls, fout=None, cs=None):
	print '  >', url

	if cs is not None and url in cs:
		for _l in cs[url]:
			ls.append(_l)
	else:
		import urllib2

		# try 5 times
		_try = 0
		while _try < 5:
			_try += 1
			try:
				_url = urllib2.urlopen(url)
				break
			except Exception:
				print '   * failed (%s)' % _try

		import re
		for _l in _url.readlines():
			_m = re.search('<a href=\"(.+)\">(.+)</a>', _l)
			if _m:
				_href = _m.group(1)
				_text = _m.group(2)

				_link = url + ('' if url.endswith('/') else '/') + _href
				if _text.endswith('.hdf'):
					ls.append(_link)
				elif _text.endswith('/'):
					if not re.match('\d+\.\d+\.\d+', _text):
						continue

					download_folder_http(_link, ls, fout, cs)

	if fout != None:
		print 'found', len(ls), 'files'
		fout.write('\n'.join(ls))
		fout.write('\n')
		ls.clear()

def download_list_http(url, f_out, _cs):
	print 'search', url

	with open(f_out, 'w') as _f:
		import collections
		_ls = collections.deque()
		download_folder_http(url, _ls, _f, _cs)

		# _ls.sort()
		# print 'found', len(_ls), 'files'

		# _f.write('\n'.join(_ls))

def download_list_ftp(host, url, f_out):
	import ftplib, re

	_ftp = ftplib.FTP(host)
	_ftp.login('')

	print 'URL', host, url

	_ls = []
	_ftp.cwd(url)
	_ftp.retrlines('LIST', _ls.append)
	_ftp.close()

	_ds = []
	for _l in _ls:
		_m = re.match('^d.+\s+(\S+)$', _l)
		if _m:
			_ds.append(_m.group(1))

	print 'write to', f_out
	open(f_out, 'w').write('\n'.join(['ftp://' + host + url + ('' if url.endswith('/') else '/') + _d for _d in _ds]))

def download_modis_product(host, dtype, code, fd_out, fa):
	import datetime, os

	_f_out = os.path.join(fd_out, code + '_' + datetime.datetime.now().strftime('%y%m%d') + '.txt')

	_url = '/' + dtype + '/' + code
	# download_list_ftp(host, _url, _f_out)

	import file_unzip
	with file_unzip.file_unzip() as _zip:

		_cs = None if not fa else _load_list(_zip.unzip(fa))

		_url = 'http://%s/%s/%s' % (host, dtype, code)
		download_list_http(_url, _f_out, _cs)

def main():
	_opts = _init_env()

	download_modis_product(_opts.host, _opts.dtype, _opts.code, _opts.output, _opts.append)

def _usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--logging', dest='logging')
	_p.add_argument('--config', dest='config')
	_p.add_argument('--debug', dest='debug', action='store_true')
	_p.add_argument('--temp', dest='temp')

	_p.add_argument('--host', dest='host', default='e4ftl01.cr.usgs.gov')
	_p.add_argument('--dtype', dest='dtype', default='MOLT', choices=['MOLT', 'MODIS_Composites', 'MOTA'])
	_p.add_argument('-c', '--code', dest='code', required=True)
	_p.add_argument('-o', '--output', dest='output', default='list')
	_p.add_argument('-a', '--append', dest='append')

	return _p.parse_args()

def _init_env():
	import os, sys

	_dirs = ['lib', 'libs']
	_d_ins = [os.path.join(sys.path[0], _d) for _d in _dirs if \
			os.path.exists(os.path.join(sys.path[0], _d))]
	sys.path = [sys.path[0]] + _d_ins + sys.path[1:]

	_opts = _usage()

	import config
	config.load(_opts.config)

	if not config.cfg.has_section('conf'):
		config.cfg.add_section('conf')

	if not _opts.logging and 'output' in _opts:
		_opts.logging = os.path.join(_opts.output, 'log.txt')

	for _k, _v in _opts.__dict__.items():
		if _v != None:
			config.cfg.set('conf', _k, str(_v))

	import logging_util
	logging_util.init(_opts.logging)

	import file_unzip as fz
	fz.clean(fz.default_dir(_opts.temp))

	return _opts

if __name__ == '__main__':
	main()

