import time
import struct

import usb.core
import usb.util

from .pat_entry import PATEntry
from .image import Image
from .video import Video

USB_REQUEST_NUM = 12

CMD_RESET = 0x00a0
CMD_GET_ID_CTRL = 0x14f4
CMD_GET_ID_BLK = 0x14f0

CMD_GET_PAT = 0x0020
CMD_GET_DSC = 0x0030

REG_CAMINFO = 0x00f5
CAMINFO_LENGTH = 20

SENSOR_INFO = {
	0x00: {
		0x00: (0x00, "PC"),
		0x03: (0x15, "SOI666"),
		0x05: (0x11, "MI0111"),
		0x13: (0x13, "PAS6101"),
	},
	0x01: {
		0x00: (0x02, "PV"),
		0x01: (0x05, "HVE"),
		0x02: (0x04, "IV"),
		0x03: (0x09, "OV7630"),
		0x05: (0x06, "MI0343"),
		0x06: (0x08, "TAS5130"),
		0x0c: (0x01, "HVD"),
		0x0d: (0x07, "MI0360"),
		0x0e: (0x0f, "H7131R"),
		0x0f: (0x10, "MI0330"),
		0x11: (0x12, "PAS302"),
		0x12: (0x0a, "OV7648"),
		0x14: (0x14, "PAS6302"),
	},
	0x03: {
		0x00: (0x0b, "PASXGA"),
		0x03: (0x0d, "OV9630SXGA"),
		0x05: (0x0e, "MI1300SXGA"),
		0x0b: (0x0c, "OV9620SXGA"),
	},
}

class Camera:
	def __init__(self):
		self.dev = usb.core.find(idVendor=0x2770)

		if self.dev is None:
			raise ValueError('Device not found')

		if self.dev.is_kernel_driver_active(0):
			self.dev.detach_kernel_driver(0)

		self.dev.set_configuration()

		self.download_caminfo()

	def __str__(self):
		return (f"Asic:0x{self.asic:04x}, "
			f"Firmware:0x{self.fw_version:02x}, "
			f"Date Code:{self.date}, "
			f"PAT Size:{self.pat_size}, "
			f"Sensor Type:0x{self.sensor_type:02x}, "
			f"Sensor ID:0x{self.sensor_id:02x}, "
			f"Sensor: {SENSOR_INFO[self.sensor_type][self.sensor_id][1]}, "
			f"Memory:{self.memory} Bytes")


	def reset(self):
		self.dev.ctrl_transfer(0x40, USB_REQUEST_NUM, CMD_RESET, 0)
		time.sleep(0.2)

	def download_caminfo(self):
		self.reset()
		self.dev.ctrl_transfer(0x40, USB_REQUEST_NUM, CMD_GET_ID_CTRL, 0)
		self.caminfo = self.dev.ctrl_transfer(0xC0, USB_REQUEST_NUM, REG_CAMINFO, 0, CAMINFO_LENGTH)
		self.reset()

		self._parse_caminfo()

	def download_caminfo_blk(self):
		self.reset()
		self.dev.ctrl_transfer(0x40, USB_REQUEST_NUM, CMD_GET_ID_BLK, 0)
		self.caminfo = self.dev.read(0x81, CAMINFO_LENGTH)
		self.reset()

		self._parse_caminfo()


	def _parse_caminfo(self):
		info = struct.unpack("<B2sB10sBBB3s", self.caminfo)

		if info[0] != CAMINFO_LENGTH:
			raise IOError("Can't read camera info")

		self.asic = int.from_bytes(info[1], "big")
		self.fw_version = info[2]
		self.date = info[3].decode("ascii")
		self.pat_size = info[4]<<6
		self.sensor_type = info[5]
		self.sensor_id = info[6]
		self.memory = int.from_bytes(info[7], "little")


	def download_pat(self):
		pat_length = self.pat_size * 16

		self.reset()
		self.dev.ctrl_transfer(0x40, USB_REQUEST_NUM, CMD_GET_PAT, pat_length>>8)
		pat_data = self.dev.read(0x81, pat_length)
		self.reset()

		self.pat = []

		for (data,) in struct.iter_unpack("<16s", pat_data):
			if data[0] == 0x00:
				break

			pat_entry = PATEntry(self, data)
			if pat_entry.valid:
				self.pat.append(pat_entry)

	def download_dsc(self):
		self.reset()
		self.dev.ctrl_transfer(0x40, USB_REQUEST_NUM, CMD_GET_DSC)

		self.images = []
		self.videos = []

		vid_frames = []
		vid_block = 0

		for pat_entry in self.pat:
			if pat_entry.is_video == False:
				if pat_entry.block_num != vid_block:
					if vid_block != 0:
						video = Video(self, vid_frames)
						self.videos.append(video)

					vid_frames = []
					vid_block = pat_entry.block_num

				data = self.dev.read(0x81, pat_entry.size)

				image = Image(self, pat_entry, data)
				if pat_entry.block_num == 0:
					self.images.append(image)
				else:
					vid_frames.append(image)
			else:
				vid_frames = []
				for frame in range(pat_entry.num_frames):
					data = self.dev.read(0x81, pat_entry.size)

					image = Image(self, pat_entry, data)
					vid_frames.append(data)

				video = Video(self, vid_frames)
				self.videos.append(video)

				vid_frames = []

		if vid_block != 0:
			video = Video(self, vid_frames)
			self.videos.append(video)

		self.reset()
