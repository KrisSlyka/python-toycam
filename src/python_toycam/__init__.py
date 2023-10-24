import argparse

from . import camera

def main():
	parser = argparse.ArgumentParser(
		description="Download images and videos from supported SQ chipset based toy cameras.",
		epilog="If no download action is specified camera contents will be listed.",
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	parser.add_argument("-d", "--debug", dest="debug", help="Print debug information like camera info and PAT content", action="store_true")
	parser.add_argument("-q", "--quiet", dest="quiet", help="Be quiet, don't print any status information", action="store_true")

	parser.add_argument("-i", "--images", dest="images", help="Download images from camera", action="store_true")
	parser.add_argument("--if", dest="image_filename", help="Image file name format", action="store", default="%03d.png", type=str)
	parser.add_argument("-r", "--raw", dest="raw", help="Save raw images instead of PNGs", action="store_true")
	parser.add_argument("--rf", dest="raw_filename", help="Raw image file name format", action="store", default="%03d.raw", type=str)

	parser.add_argument("-v", "--videos", dest="videos", help="Download videos from camera", action="store_true")
	parser.add_argument("--vf", dest="video_filename", help="Video file name format", action="store", default="%03d.mp4", type=str)
	parser.add_argument("-f", "--fps", dest="fps", action="store", help="FPS for saved videos", default=12, type=float)
	parser.add_argument("-s", "--scale", dest="scale", action="store", help="Nearest neighbor upscale downloaded videos x times", default=4, type=float)

	parser.add_argument("-g", "--gamma", dest="gamma", help="Image/video gamma adjustment", action="store", default=2.0, type=float)

	args = parser.parse_args()

	if not args.quiet:
		print("Connecting...")

	cam = camera.Camera()

	if args.debug:
		print(cam)

	if not args.quiet:
		print("Reading Picture Allocation Table...")

	cam.download_pat()

	if args.debug:
		for entry in cam.pat:
			print(entry)

	if not args.quiet:
		print("Reading Image Data...")

	cam.download_dsc()

	if not (args.images or args.videos):
		if not args.quiet:
			print("Images:")

		for num, image in enumerate(cam.images):
			pe = image.pat_entry
			print(f"Image {num:03d}: {pe.width}x{pe.height} px, {'compressed' if pe.is_compressed else 'uncompressed'}, {pe.size} bytes")

		if not args.quiet:
			print("Videos:")

		for num, video in enumerate(cam.videos):
			print(f"Video {num:03d}: {video.width}x{video.height} px, {len(video.frames)} frames, {video.size} bytes")

	if args.images:
		for num, image in enumerate(cam.images):
			if not args.quiet:
				if args.raw:
					print(f"Processing image {args.raw_filename % num}")
				else:
					print(f"Processing image {args.image_filename % num}")

			image.decompress()

			if args.raw:
				with open(args.raw_filename % num, "wb+") as f:
					f.write(image.raw)
			else:
				image.develop(args.gamma)
				image.image.save(args.image_filename % num, quality=96, optimize=True)

	if args.videos:
		for num, video in enumerate(cam.videos):
			if not args.quiet:
				print(f"Processing video {args.video_filename % num}")

			video.process(args.gamma)
			video.encode(args.video_filename % num, args.fps, args.scale)
