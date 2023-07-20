from typing import List, Tuple
from fontTools.ttLib import TTFont

class Finder:
	"""グリフ名からグリフIDを取得する"""

	def __init__(self, font: TTFont, verbose: bool = False):
		self.font = font
		self.cmap = font.getBestCmap()
		self.verbose = verbose

	def getCID(self, letter: str) -> str:
		if len(letter) == 0:
			raise ValueError("Letter is empty.")

		codePoint = ord(letter[0])
		if codePoint not in self.cmap:
			raise ValueError(f"Letter '{letter}' not found in the font.")
		cid = self.cmap[codePoint]

		if len(letter) > 1:
			features = letter[2:].split('.')
			for feature in features:
				cid = self.lookupFeature(cid, feature)

		return cid

	def lookupFeature(self, cid: str, feature: str) -> str:
		if 'GSUB' not in self.font:
			if self.verbose:
				print('Warning: GSUB table not found.')
			return cid

		gsub = self.font['GSUB'].table
		lookupIndexes = None
		for featureRecord in gsub.FeatureList.FeatureRecord:
			if featureRecord.FeatureTag == feature:
				if type(featureRecord.Feature.LookupListIndex) == list:
					lookupIndexes = featureRecord.Feature.LookupListIndex
				else:
					lookupIndexes = [featureRecord.Feature.LookupListIndex]
				break
		if lookupIndexes is None:
			if self.verbose:
				print(f"Warning: フィーチャー '{feature}' が見つかりません")
			return cid

		for lookupIndex in lookupIndexes:
			lookup = gsub.LookupList.Lookup[lookupIndex]
			for subTable in lookup.SubTable:
				if subTable.LookupType == 9: # Extension Substitution
					subTable = subTable.extSubTable
				if subTable.LookupType == 1: # Single Substitution
					if cid in subTable.mapping:
						return subTable.mapping[cid]
				else:
					if self.verbose:
						print(f"Warning: {cid} に対するルックアップタイプ {subTable.LookupType} はサポートされていません")

		if self.verbose:
			print(f"Warning: {cid} に対するフィーチャー '{feature}' が見つかりません")
		return cid
