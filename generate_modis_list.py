

def generate_modis_urls(f_urls, tiles, years, f_out):
	import re

	print 'tiles:', tiles
	print 'years:', years

	_ls = []
	for _l in open(f_urls).read().splitlines():
		if _l:
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
		open(f_out, 'w').write('\n'.join(_ls))

def usage():
	import argparse

	_p = argparse.ArgumentParser()

	_p.add_argument('-f', '--file-urls', dest='fileurls', default='MOD09GA_20111010.txt')
	_p.add_argument('-y', '--year', dest='year', type=int, action='append', default=[])
	_p.add_argument('-t', '--tiles', dest='tiles', nargs='*', default=[])
	_p.add_argument('-o', '--output', dest='output', required=True)

	return _p.parse_args()

if __name__ == '__main__':
	_opts = usage()
	generate_modis_urls(_opts.fileurls, _opts.tiles, _opts.year, _opts.output)



