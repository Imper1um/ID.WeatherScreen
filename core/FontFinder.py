from PIL import ImageFont
from fontTools.ttLib import TTFont
import os
import glob
import logging

from .Platform import Platform

class FontFinder:
    FontPathCache = {}
    Log = logging.getLogger("FontFinder")

    def GetFont(fontFamily: str, fontSize: int):
        fontFamilyKey = fontFamily.lower().replace(' ', "")

        if fontFamilyKey in FontFinder.FontPathCache:
            cachedPath = FontFinder.FontPathCache[fontFamilyKey]
            try:
                return ImageFont.truetype(cachedPath, fontSize)
            except Exception as e:
                logging.warning(f"Failed to load cached font '{fontFamily}' from '{cachedPath}': {e}")
                del FontFinder.FontPathCache[fontFamilyKey]  # Remove bad entry

        system = "pi" if Platform.IsRaspberryPi() else "windows"

        searchPaths = []
        if system == "windows":
            searchPaths = [r"C:\Windows\Fonts"]
        else:
            searchPaths = [
                "/usr/share/fonts/truetype",
                "/usr/share/fonts",
                "/usr/local/share/fonts"
            ]

        fontFamilyLower = fontFamily.lower().replace(" ", "")
        matchedPath = None

        for path in searchPaths:
            for fontFile in glob.glob(os.path.join(path, "**", "*.ttf"), recursive=True):
                try:
                    filename = os.path.basename(fontFile).lower().replace(" ", "")
                    if fontFamilyLower in filename:
                        matchedPath = fontFile
                        break

                    tt = TTFont(fontFile, fontNumber=0)
                    names = tt["name"].names
                    for record in names:
                        try:
                            name = record.string.decode("utf-16-be" if record.platformID == 0 or record.platformID == 3 else "latin-1")
                            if fontFamilyLower in name.lower().replace(" ", ""):
                                matchedPath = fontFile
                                break
                        except Exception:
                            continue
                    if matchedPath:
                        break
                except Exception:
                    continue
            if matchedPath:
                break

        if matchedPath:
            try:
                FontFinder.FontPathCache[fontFamilyKey] = matchedPath
                FontFinder.Log.debug(F"{fontFamily} = {fontFamilyKey} points to {matchedPath}")
                return ImageFont.truetype(matchedPath, fontSize)
            except Exception as e:
                FontFinder.Log.warning(f"Failed to load font from '{matchedPath}': {e}")

        FontFinder.Log.warning(f"Font '{fontFamily}' not found; falling back to default.")
        return ImageFont.load_default()
