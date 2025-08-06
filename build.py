from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.merge import Merger
from fontTools.varLib import builder
import os
import shutil
from copy import deepcopy

LOCALES = ["KR", "HK", "TC", "SC", "JP"] # This is an opinionated sequence of fallback
CWD = os.getcwd()

def set_name(table, text, name_id, platforms=(
	(3, 1, 0x409),
	(1, 0, 0)),
):
	for platform_id, plat_enc_id, lang_id in platforms:
		table.setName(text, name_id,
			platformID=platform_id,
			platEncID=plat_enc_id,
			langID=lang_id)

def build(style):
	print(f"Building style {style}...")
	os.chdir(CWD)
	shutil.rmtree("tmp", ignore_errors=True)
	os.mkdir("tmp")
	base_path = f"noto-cjk/{style}/Variable/TTF/Subset"

	for locale in LOCALES:
		print(f"- Building locale {locale}... Adding glyphs... ", end="", flush=True)
		base = TTFont(f"{base_path}/Noto{style}{locale}-VF.ttf")
		if 'gvar' in base: _ = base['gvar']
		for tag, fallback in [
			(l, TTFont(f"{base_path}/Noto{style}{l}-VF.ttf"))
			for l in LOCALES
			if l != locale
		]:
			print(f"{tag}... ", end="", flush=True)
			base_glyphs     = set(base.getGlyphOrder())
			fallback_glyphs = set(fallback.getGlyphOrder())
			missing         = sorted(fallback_glyphs - base_glyphs)

			if not missing: continue

			base.setGlyphOrder(base.getGlyphOrder() + missing)

			for gname in missing:
				base['glyf'][gname] = fallback['glyf'][gname]
				base['hmtx'][gname] = fallback['hmtx'][gname]
				if 'vmtx' in base and 'vmtx' in fallback:
					base['vmtx'][gname] = fallback['vmtx'][gname]

				if 'gvar' in base and 'gvar' in fallback:
					varData = fallback['gvar'].variations.get(gname)
					if varData is not None:
						base['gvar'].variations[gname] = deepcopy(varData)

			if 'gvar' in base: base['gvar'].glyphCount = len(base.getGlyphOrder())

			for cmapTable in fallback['cmap'].tables:
				for uni, gname in cmapTable.cmap.items():
					if gname in missing:
						target = next(
							(t for t in base['cmap'].tables
							if (t.platformID, t.platEncID) ==
								(cmapTable.platformID, cmapTable.platEncID)),
							None
						)
						if not target:
							target = cmapTable.__class__()
							target.platformID, target.platEncID = cmapTable.platformID, cmapTable.platEncID
							target.language, target.cmap = cmapTable.language, {}
							base['cmap'].tables.append(target)
						target.cmap[uni] = gname

			base['maxp'].numGlyphs = len(base.getGlyphOrder())
		print("Saving... ", end="", flush=True)
		name = base['name']
		family = f"Noto {style} CJK {locale} Pinned"
		full = f"{family}"
		post = f"Noto{style}CJK{locale}Pinned"
		set_name(name, family, 1)
		set_name(name, full, 4)
		set_name(name, post, 6)
		set_name(name, family, 16)
		set_name(name, family, 21)
		base.save(f"tmp/Noto{style}CJK{locale}Pinned.ttf")
		print("Done.")
	shutil.rmtree(style, ignore_errors=True)
	shutil.move("tmp", style)
	print("Done.")
	print()

if __name__ == "__main__":
	build("Sans")
	build("Serif")
