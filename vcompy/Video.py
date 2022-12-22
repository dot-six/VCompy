import math

import numpy as np
import imageio.v3 as iio

from PIL import Image

from .Media import Media

def pts_to_frame(pts, time_base, frame_rate, start_time):
	return int(pts * time_base * frame_rate) - int(start_time * time_base * frame_rate)


class Video(Media):
	def __init__(self, fps=24, **kwargs):
		super().__init__(**kwargs)

		self.fps = fps
		self.img = None
		self.metadata = dict()

		self.keyframe_interval = 0.10

	@staticmethod
	def from_file(path):
		v = Video()
		v.img = iio.imopen(path, 'r', plugin="pyav")

		v.metadata = v.img.metadata()
		v.fps = v.metadata['fps']

		v.duration = v.metadata['duration'] * v.fps

		return v

	def get_frame(self, i, format='rgb24'):
		if self.img is None:
			raise Exception('Video self.img unset')

		timebase = self.img._container.streams.video[0].time_base

		# Convert frameIndex to pts
		targetSec = i / self.fps
		targetPts = int((targetSec - self.keyframe_interval) / timebase) # + start_time

		self.img._container.seek(int(targetPts), any_frame=True)

		def next_frame():
			framei = None
			for packet in self.img._container.demux(video=0):
				for frame in packet.decode():
					print(frame)
					if frame.pts:
						pts = frame.pts
					else:
						pts = frame.dts

					if framei is None:
						framei = pts_to_frame(pts, timebase, self.fps, 0) # TODO start time
					elif not framei is None:
						# Normally count up frame number
						framei += 1
					yield framei, frame

		for framei, frame in next_frame():
			if framei == i:
				# match!
				return self.img._unpack_frame(frame, format=format)
		# No match :(
		return None

	def get_frame_pil(self, i, format='rgb24'):
		frame = self.get_frame(i, format=format)

		if frame is None:
			return None
		return Image.fromarray(frame)
