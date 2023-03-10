from os import path

from .Overlay import Overlay

class Text(Overlay):
	def __init__(self, text=None, font=None, fontsize=16, color=(0, 0, 0), anchor='la', align='left', **kwargs):
		super().__init__(**kwargs)

		self.text = text
		self.fontsize = fontsize
		self.font = font
		self.color = color
		self.anchor = anchor
		self.align = align

		if not path.exists(font):
			raise Exception(f"Font {font} does not exists")
