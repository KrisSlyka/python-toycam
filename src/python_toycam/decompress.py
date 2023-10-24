VLC_PREFIXES = [-1,0x00,0x02,0x06,0x0e,0x0e,0x0e,0x0e,0xfb]
VLC_LUT = {
	0x00: 0x08,
	0x02: 0x07,
	0x06: 0x09,
	0x0e: 0x06,
	0xf0: 0x0A,
	0xf1: 0x0B,
	0xf2: 0x0C,
	0xf3: 0x0D,
	0xf4: 0x0E,
	0xf5: 0x0F,
	0xf6: 0x05,
	0xf7: 0x04,
	0xf8: 0x03,
	0xf9: 0x02,
	0xfa: 0x01,
	0xfb: 0x00,
}

ADPCM_LUT = [
	-0x90,
	-0x6e,
	-0x4d,
	-0x35,
	-0x23,
	-0x15,
	-0xb,
	-3,
	2,
	10,
	0x14,
	0x22,
	0x34,
	0x4c,
	0x6e,
	0x90,
]

def vlc_decode(in_buf, width, height):
	in_byte = 0
	in_bytes = iter(in_buf)
	out_buf = bytearray()
	bit = 8

	while len(out_buf) < width * height:
		i = 0
		code = 0
		while code > VLC_PREFIXES[i]:
			if bit==8:
				in_byte = next(in_bytes)
				bit = 0

			code = ((code << 1) | (in_byte >> 7)) & 0xff
			in_byte = (in_byte << 1 ) & 0xff
			bit += 1
			i += 1

		out_buf.append(VLC_LUT[code])

	return out_buf


# Somebody should reimplement this in numpy or something
def adpcm_1_decode(in_buf, width, height):
	r_line = [0x80]*(width//2)
	g_line = [0x80]*(width//2)
	b_line = [0x80]*(width//2)

	raw_image = bytearray()

	in_bytes = iter(in_buf)

	for y in range(0, height):
		if y%2 == 0:
			r = r_line[0]
			g = g_line[1]
			for x in range(0, width//2):
				delta = ADPCM_LUT[next(in_bytes)]
				r = (r + r_line[x]) // 2 + delta
				r = max(0, min(r, 0xff))
				r_line[x] = r
				raw_image.append( r )

				delta = ADPCM_LUT[next(in_bytes)]
				g = (g + g_line[min(x+1, width//2-1)]) // 2 + delta
				g = max(0, min(g, 0xff))
				g_line[x] = g
				raw_image.append( g )
		else:
			g = g_line[0]
			b = b_line[0]
			for x in range(0, width//2):
				delta = ADPCM_LUT[next(in_bytes)]
				g = (g + g_line[x]) // 2 + delta
				g = max(0, min(g, 0xff))
				g_line[x] = g
				raw_image.append( g )

				delta = ADPCM_LUT[next(in_bytes)]
				b = (b + b_line[x]) // 2 + delta
				b = max(0, min(b, 0xff))
				b_line[x] = b
				raw_image.append( b )

	return raw_image
