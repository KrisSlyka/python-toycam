import struct

# width, height, compressed, bytes per pixel, video
IMG_TYPES = {
	'A': (352,  288,  False, 1, False,),
	'a': (352,  288,  True,  1, False,),
	'B': (176,  144,  False, 1, False,),
	'b': (176,  144,  True,  1, False,),
	'C': (320,  240,  False, 1, False,),
	'c': (320,  240,  True,  1, False,),
	'L': (1027, 768,  False, 1, False,),
	'l': (1027, 768,  True,  1, False,),
	'M': (1280, 960,  False, 1, False,),
	'm': (1280, 960,  False, 1, False,),
	'g': (1280, 960,  True,  1, False,),
	'N': (1600, 1200, False, 1, False,),
	'n': (1600, 1200, True,  1, False,),
	'Q': (160,  120,  False, 1, False,),
	'R': (352,  288,  False, 1, True, ),
	'S': (320,  240,  False, 1, True, ),
	'U': (640,  480,  False, 2, False,),
	'V': (640,  480,  False, 1, False,),
	'v': (640,  480,  True,  1, False,),
	'Y': (320,  240,  False, 2, False,),
	'r': (176,  144,  False, 1, True, ),
	's': (160,  120,  False, 1, True, ),
	}

class PATEntry:
	def __init__(self, camera, data):
		self.type = chr(data[0])
		self.camera = camera

		if self.type not in IMG_TYPES.keys():
			self.valid = False
			return
		else:
			self.valid = True

		(width, height, comp, bpp, vid) = IMG_TYPES[self.type]

		self.width = width
		self.height = height
		self.is_compressed = comp
		self.bytes_per_pixel = bpp
		self.is_video = vid

		if self.is_video == False:
			(psp, psah, psal, size, fst_clus, ev, y, r, g1, b, block_num) = struct.unpack("<xBBBIHBBBBBB", data)
			self.data_size = size
			self.num_frames = 1
			self.block_num = block_num
			self.image_info = {
				"psp": psp,
				"psah": psah,
				"psal": psal,
				"fst_clus": fst_clus,
				"ev": ev,
				"y": y,
				"r": r,
				"g1": g1,
				"b": b,
			}
		else:
			(nf,) = struct.unpack("<xxxxxxxHxxxxxxx", data)
			self.num_frames = nf
			self.block_num = 1
			self.image_info = {}

		if self.is_compressed == True and self.is_video == False:
			self.size = self.data_size
		else:
			self.size = self.width * self.height * self.bytes_per_pixel


	def __str__(self):
		return (f"Type:{self.type}, "
			f"Res:{self.width}x{self.height}, "
			f"Compressed:{self.is_compressed}, "
			f"BPP:{self.bytes_per_pixel}, "
			f"Video:{self.is_video}, "
			f"Frames:{self.num_frames}, "
			f"Block #:{self.block_num}, "
			f"Size:{self.size}")
