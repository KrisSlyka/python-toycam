# python-toycam

A small tool and python library to work with early 2000s digital toy cameras based on chipsets made by Service & Quality Technology like the SQ905C and SQ913D.

Most of this was directly reverse engineered from the windows driver but not all compression formats are implemented. What's here should cover most cameras though.

Some of these cameras are also supported by libgphoto2, but their driver is kinda janky. The webcam mode these cameras have seem to work fine through the kernel drivers, so I didn't reimplement that part here.

## Installation

```
pipx install .
```

## Usage

```
usage: toycam [-h] [-d] [-q] [-i] [--if IMAGE_FILENAME] [-r] [--rf RAW_FILENAME] [-v] [--vf VIDEO_FILENAME] [-f FPS] [-s SCALE] [-g GAMMA]

Download images and videos from supported SQ chipset based toy cameras.

options:
  -h, --help            show this help message and exit
  -d, --debug           Print debug information like camera info and PAT content (default: False)
  -q, --quiet           Be quiet, don't print any status information (default: False)
  -i, --images          Download images from camera (default: False)
  --if IMAGE_FILENAME   Image file name format (default: %03d.png)
  -r, --raw             Save raw images instead of PNGs (default: False)
  --rf RAW_FILENAME     Raw image file name format (default: %03d.raw)
  -v, --videos          Download videos from camera (default: False)
  --vf VIDEO_FILENAME   Video file name format (default: %03d.mp4)
  -f FPS, --fps FPS     FPS for saved videos (default: 12)
  -s SCALE, --scale SCALE
                        Nearest neighbor upscale downloaded videos x times (default: 4)
  -g GAMMA, --gamma GAMMA
                        Image/video gamma adjustment (default: 2.0)

If no download action is specified camera contents will be listed.
```