from streaming.config import ConfigManager
from media import MediaLibrary

config = ConfigManager()

lib = MediaLibrary(config.media_series_dir)

data = lib.get_structure()

print("RESULTADO:")
print(data)