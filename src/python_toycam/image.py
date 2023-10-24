from PIL import Image as PILImage

from . import decompress
from . import debayer

class Image:
	def __init__(self, camera, pat_entry, data):
		self.camera = camera
		self.pat_entry = pat_entry
		self.data = data

		self.width = pat_entry.width
		self.height = pat_entry.height

	def decompress(self):
		if self.pat_entry.is_compressed == False:
			self.raw = self.data
		else:
			if self.pat_entry.type == 'g':
				if self.camera.asic == 0x0906:
					raise NotImplementedError("Chunked decompression mode 3 is not supported yet!")
				else:
					raise NotImplementedError("Chunked decompression mode 1 is not supported yet!")
			else:
				vlc_data = decompress.vlc_decode(self.data, self.width, self.height)

				if self.camera.asic == 0x0906 and self.pat_entry.type == 'c' and camera.fw_version == 0x13:
					raise NotImplementedError("Decompression mode 4 is not supported yet!")
				else:
					self.raw = decompress.adpcm_1_decode(vlc_data, self.width, self.height)

	def develop(self, gamma = 2.0):
		if self.pat_entry.bytes_per_pixel == 1:
			self.pixels = debayer.debayer(self.raw, self.width, self.height, gamma)
		else:
			raise NotImplementedError("16bpp images are not supported yet!")

		self.image = PILImage.frombytes("RGB", (self.width, self.height), self.pixels)
