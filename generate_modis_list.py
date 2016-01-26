'''
File: generate_modis_list.py
Author: Min Feng
Version: 0.1
Create: 2016-01-26 14:59:23
Description: generate a list of MODIS data for given years, tile
'''

def generate_modis_urls(f_url, tiles, years, f_out):
	import re

	print 'tiles:', tiles
	print 'years:', years

	_ls = []

	import gzip
	with gzip.open(f_url, 'r') if f_url.endswith('.gz') else open(f_url, 'r') as _fi:
		for _l in _fi.read().splitlines():
			_l = _l.strip()
			if not _l:
				continue

			_r = re.search('A(\d{4})\d{3}\.(h\d{2}v\d{2})', _l)

			_t = _r.group(2)
			_y = int(_r.group(1))

			if len(years) > 0 and _y not in years:
				continue

			if len(tiles) > 0 and _t not in tiles:
				continue

			_ls.append(_l)

	print 'found', len(_ls), 'files'
	if len(_ls):
		with gzip.open(f_out, 'w') if f_out.endswith('.gz') else open(f_out, 'w') as _fo:
			_fo.write('\n'.join(_ls))

def usage():
	import argparse

	_p = argparse.ArgumentParser()

	_p.add_argument('-i', '--file-urls', dest='fileurls')
	_p.add_argument('-y', '--year', dest='year', type=int, nargs='*', default=[])
	_p.add_argument('-t', '--tiles', dest='tiles', nargs='*', default=[])
	_p.add_argument('-o', '--output', dest='output', required=True)

	return _p.parse_args()

if __name__ == '__main__':
	_opts = usage()
	generate_modis_urls(_opts.fileurls, _opts.tiles, _opts.year, _opts.output)



