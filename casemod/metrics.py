import sys
from typing import List, Tuple
from fontTools.ttLib import TTFont

from finder import Finder

class MetricsReader:
	def __init__(self, font: TTFont):
		self.font = font
		self.cmap = font.getBestCmap()

	def getGlyphMetrics(self, cid: str) -> Tuple[int, int, int, int]:
		"""指定した文字のグリフのメトリクスを取得します"""

		if 'glyf' in self.font:
			glyfTable = self.font['glyf'].glyphs
			if cid not in glyfTable:
				raise ValueError(f"Glyph '{cid}' not found in the font.")
			glyph = glyfTable[cid]

			if glyph.isComposite():
				raise ValueError(f"Composite glyph '{cid}' is not supported.")

			return glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax

		elif 'CFF ' in self.font:
			charStrings = self.font['CFF '].cff.topDictIndex[0].CharStrings
			if cid not in charStrings:
				raise ValueError(f"Glyph '{cid}' not found in the font.")
			glyph = charStrings[cid]
			return glyph.calcBounds(None)

if __name__ == "__main__":
	fontFile: str = ''
	fontNumber: int = 0
	letters: List[str] = []

	error = False
	flag = ''
	for index, arg in enumerate(sys.argv):
		if index == 0:
			continue
		if arg[0] == '-':
			flag = arg[1:]
			if flag not in {'n'}:
				print('Unknown flag: -%s' % (flag))
				error = True
				break
			continue
		if flag != '':
			if flag == 'n':
				fontNumber = int(arg)
			flag = ''
		else:
			if fontFile == '':
				fontFile = arg
			else:
				letters.append(arg)

	if fontFile == '' or error:
		print('グリフのメトリクスを取得します')
		print('')
		print('Usage:')
		print('    python metrics.py <OPTIONS> <FILE> <LETTER>...')
		print('')
		print('Options:')
		print('    -n <NUMBER>    TTCのフォントの番号を指定します')
		sys.exit()

	font = TTFont(fontFile, fontNumber=fontNumber)
	finder = Finder(font)
	reader = MetricsReader(font)
	for letter in letters:
		cid = finder.getCID(letter)
		xmin, ymin, xmax, ymax = reader.getGlyphMetrics(cid)
		print(f'{letter}\tx: [{xmin}, {xmax}]\ty: [{ymin}, {ymax}]')
