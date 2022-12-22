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

		self.resourcePath = None

		self.fps = fps
		self.img = None
		self.metadata = dict()

		self.clip_start = 0

		self.keyframe_interval = 0.10
		self._frames = []

	@staticmethod
	def from_file(path, cacheframes=False):
		v = Video()

		v.resourcePath = path
		v.img = iio.imopen(path, 'r', plugin="pyav")

		v.metadata = v.img.metadata()
		v.fps = v.metadata['fps']

		v.duration = v.metadata['duration'] * v.fps

		if cacheframes:
			v.cache_frames()

		return v

	def sub_clip(self, start, end=None, cacheframes=True):
		# end defaults to self.duration
		if end is None:
			duration = self.duration
		else:
			duration = abs(end - start)
		self.duration = duration

		self.clip_start = start

		if cacheframes:
			self.cache_frames()

		return self

	def sub_clip_copy(self, start, end=None, cacheframes=True):
		v = Video.from_file(self.resourcePath)

		return v.sub_clip(start, end, cacheframes=cacheframes)

	def cache_frame(self, frame, i):
		framesLen = len(self._frames)
		if i >= framesLen:
			dl = framesLen + 1 - i
			for _ in range(dl):
				self._frames.append(None)

		self._frames[i] = frame

	def cache_frames(self):
		timebase = self.img._container.streams.video[0].time_base

		framei = None
		for packet in self.img._container.demux(video=0):
			for frameo in packet.decode():
				if frameo.pts:
					pts = frameo.pts
				else:
					pts = frameo.dts

				if framei is None:
					framei = pts_to_frame(pts, timebase, self.fps, 0) # TODO start time
				elif not framei is None:
					# Normally count up frame number
					framei += 1

				# sub clipping
				if framei >= self.clip_start and framei < self.clip_start + self.duration:
					self.cache_frame(frameo, framei - self.clip_start)
				elif framei >= self.clip_start + self.duration:
					return
				else:
					...

	def get_frame(self, i, format='rgb24'):
		if self.img is None:
			raise Exception('Video self.img unset')

		frame = None

		if i < len(self._frames):
			frame = self.img._unpack_frame(self._frames[i], format=format)

		return frame

	def get_frame_pil(self, i, format='rgb24'):
		frame = self.get_frame(i, format=format)

		if frame is None:
			return None
		return Image.fromarray(frame)
