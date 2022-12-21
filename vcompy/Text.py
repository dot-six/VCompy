from os import path

from .Overlay import Overlay

class Text(Overlay):
	def __init__(self, text=None, font=None, fontsize=16, **kwargs):
		super.__init__(**kwargs)

		self.text = text
		self.fontsize = fontsize
		self.font = font

		if not path.exists(font):
			raise Exception(f"Font {font} does not exists")
