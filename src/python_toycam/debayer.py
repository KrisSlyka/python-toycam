import numpy as np

# Sorry to whoever has to make sense of this…
def debayer(in_buffer, width, height, gamma):
	in_pixels = np.array(in_buffer, dtype=float).reshape((height, width))
	out_pixels = np.zeros((height, width, 3))

	r = in_pixels[0::2,0::2]
	out_pixels[0::2, 0::2, 0] = r[0::, 0::]
	out_pixels[0::2, 1:-1:2, 0] = (r[::, :-1:] + r[::, 1::]) / 2
	out_pixels[1:-1:2, 0::2, 0] = (r[:-1:, ::] + r[1::, ::]) / 2
	out_pixels[1:-1:2, 1:-1:2, 0] = (r[:-1:, :-1:] + r[1::, 1::] + r[1::, :-1:] + r[:-1:, 1::]) / 4
	out_pixels[::, -1, 0] = out_pixels[::, -2, 0]
	out_pixels[-1, ::, 0] = out_pixels[-2, ::, 0]


	g1 = in_pixels[0::2,1::2]
	g2 = in_pixels[1::2,0::2]
	out_pixels[0::2, 1::2, 1] = g1[0::, 0::]
	out_pixels[1::2, 0::2, 1] = g2[0::, 0::]
	out_pixels[1:-1:2, 1:-1:2, 1] = (g1[:-1:, 0:-1:] + g1[1::, 0:-1:] + g2[0:-1:, :-1:] + g2[0:-1:, 1::]) / 4
	out_pixels[2:-1:2, 2:-1:2, 1] = (g2[:-1:, 1::] + g2[1::, 1::] + g1[1::, :-1:] + g1[1::, 1::]) / 4
	out_pixels[2::2, 0, 1] = (g2[:-1:, 0] + g2[1::, 0] + g1[1::, 0]) / 3
	out_pixels[1:-1:2, -1, 1] = (g1[:-1:, -1] + g1[1::, -1] + g2[:-1:, -1]) / 3
	out_pixels[0, 2:-1:2, 1] = (g2[0, 1::] + g1[0, :-1:] + g1[0, 1::]) / 3
	out_pixels[-1, 1:-1:2, 1] = (g1[-1, 0:-1:] + g2[-1, :-1:] + g2[-1, 1::]) / 3
	out_pixels[0, 0, 1] = (g1[0, 0] + g2[0, 0]) / 2
	out_pixels[-1, -1, 1] = (g1[-1, -1] + g2[-1, -1]) / 2


	b = in_pixels[1::2,1::2]
	out_pixels[1::2, 1::2, 2] = b[0::, 0::]
	out_pixels[1::2, 2:-1:2, 2] = (b[::, :-1:] + b[::, 1::]) / 2
	out_pixels[2:-1:2, 1::2, 2] = (b[:-1:, ::] + b[1::, ::]) / 2
	out_pixels[2:-1:2, 2:-1:2, 2] = (b[:-1:, :-1:] + b[1::, 1::] + b[1::, :-1:] + b[:-1:, 1::]) / 4
	out_pixels[::, 0, 2] = out_pixels[::, 1, 2]
	out_pixels[0, ::, 2] = out_pixels[1, ::, 2]

	out_pixels = np.power(out_pixels / 255.0, 1.0/gamma) * 255.0

	return out_pixels.astype(np.byte).tobytes()
