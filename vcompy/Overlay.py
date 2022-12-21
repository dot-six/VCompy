from .Media import Media

class Overlay(Media):
	def __init__(self, size=None, position=None, **kwargs):
		super().__init__(**kwargs)

		if size is None:
			size = (0, 0)
		self.size = size

		if position is None:
			position = (0, 0)

		self.position = position
