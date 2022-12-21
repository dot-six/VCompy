import numpy as np
import imageio.v3 as iio

from .Media import Media

class Video(Media):
	def __init__(self, fps=24, **kwargs):
		super().__init__(**kwargs)

		self.fps = fps
		self.img = None

	@staticmethod
	def from_file(path):
		v = Video()
		v.img = iio.imopen(path, 'r')

		return v

	def get_frame(self, i):
		if self.img is None:
			raise Exception('Video self.img unset')

		return self.img.read(index=i)

	def get_frame_pil(self, i):
		frame = self.get_frame(i)
		return Image.fromarray(frame)
