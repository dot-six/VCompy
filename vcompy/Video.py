import numpy as np
import imageio.v3 as iio

from PIL import Image

from .Media import Media

class Video(Media):
	def __init__(self, fps=24, **kwargs):
		super().__init__(**kwargs)

		self.fps = fps
		self.img = None
		self.metadata = dict()

	@staticmethod
	def from_file(path):
		v = Video()
		v.img = iio.imopen(path, 'r', plugin="pyav")

		v.metadata = v.img.metadata()
		v.fps = v.metadata['fps']

		v.duration = v.metadata['duration'] * v.fps

		return v

	def get_frame(self, i):
		if self.img is None:
			raise Exception('Video self.img unset')

		return self.img.read(index=i)

	def get_frame_pil(self, i):
		frame = self.get_frame(i)
		return Image.fromarray(frame)
