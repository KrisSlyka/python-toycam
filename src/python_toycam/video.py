from PIL import Image as PILImage
import av

class Video:
	def __init__(self, camera, frames):
		self.camera = camera
		self.frames = frames

		self.width = frames[0].pat_entry.width
		self.height = frames[0].pat_entry.height
		self.size = 0

		for f in self.frames:
			self.size += f.pat_entry.size
			if f.pat_entry.width != self.width or f.pat_entry.height != self.height:
				raise ValueError("Inconsistent frame sizes in video!")

	def process(self, gamma = 2.0):
		for frame in self.frames:
			frame.decompress()
			frame.develop(gamma)

	def encode(self, file_name, fps=12, scale=1.0):
		container = av.open(file_name, mode="w")

		stream = container.add_stream("h264", rate=fps, options={"crf": "20"})
		stream.width = int(self.width * scale)
		stream.height = int(self.height * scale)
		stream.pix_fmt = "yuv444p"

		for frame in self.frames:
			image = frame.image

			if scale != 1.0:
				image = image.resize((int(image.width*scale), int(image.height*scale)), PILImage.Resampling.NEAREST)

			av_frame = av.VideoFrame.from_image(image)
			for packet in stream.encode(av_frame):
				container.mux(packet)

		for packet in stream.encode():
			container.mux(packet)

		container.close()