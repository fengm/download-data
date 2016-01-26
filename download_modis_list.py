'''
File: download_modis_list.py
Author: Min Feng
Version: 0.1
Create: 2016-01-26 14:58:55
Description: download MODIS data list
'''
def download_folder_http(url, ls, fout=None):
	import urllib2

	print '  >', url

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
				download_folder_http(_link, ls)

			if fout != None:
				print 'found', len(ls), 'files'
				fout.write('\n'.join(ls))
				fout.write('\n')
				ls.clear()


def download_list_http(url, f_out):
	print 'search', url

	with open(f_out, 'w') as _f:
		import collections
		_ls = collections.deque()
		download_folder_http(url, _ls, _f)

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

def download_modis_product(host, dtype, code, fd_out):
	import datetime, os

	_f_out = os.path.join(fd_out, code + '_' + datetime.datetime.now().strftime('%y%m%d') + '.txt')

	_url = '/' + dtype + '/' + code
	# download_list_ftp(host, _url, _f_out)

	_url = 'http://%s/%s/%s' % (host, dtype, code)
	download_list_http(_url, _f_out)

def usage():
	import argparse

	_p = argparse.ArgumentParser()
	_p.add_argument('--host', dest='host', default='e4ftl01.cr.usgs.gov')
	_p.add_argument('--dtype', dest='dtype', default='MOLT', choices=['MOLT', 'MODIS_Composites', 'MOTA'])
	_p.add_argument('-c', '--code', dest='code', required=True)
	_p.add_argument('-o', '--output', dest='output', default='list')

	return _p.parse_args()

if __name__ == '__main__':
	_opts = usage()
	download_modis_product(_opts.host, _opts.dtype, _opts.code, _opts.output)

