import os

from PIL import Image, ImageDraw, ImageFont
import av

from .Video import Video
from .Text import Text

class Compiler:
	TMP_FOLDER = 'vctmp'

	def __init__(self, clips, fps=None, size=None, duration=None):
		self.clips = clips

		if fps is None:
			fps = 24
		self.fps = fps

		if size is None:
			size = (640, 480)
		self.size = size

		self.duration = duration

	@staticmethod
	def simple(clips):
		c = Compiler(clips)
		return c

	def get_duration(self):
		if not self.duration is None:
			return self.duration

		duration = 0
		for clip in self.clips:
			if clip.duration > duration:
				duration = clip.duration

		return duration

	def get_clips_in_frame(self, i):
		clips = list()

		for clip in self.clips:
			if clip.start <= i and i < clip.start + clip.duration:
				clips.append(clip)

		return clips

	def save_as(self, filename):
		frameIndex = 0
		container = av.open(filename, mode='w')
		stream = container.add_stream("mpeg4", rate=self.fps)
		stream.width = self.size[0]
		stream.height = self.size[1]
		stream.pix_fmt = "yuv420p"

		try:
			os.mkdir(f"{self.TMP_FOLDER}-img-seq/")
		except:
			pass

		# Last frame where?
		duration = self.get_duration()
		while frameIndex < duration:
			frame = Image.new("RGB", self.size, (0, 0, 0))
			ctx = ImageDraw.Draw(frame)
			for clip in self.get_clips_in_frame(frameIndex):
				clipType = type(clip)
				# Video is base media, so they have (0, 0) position
				if clipType is Video:
					im = clip.get_frame_pil(frameIndex)
					frame.paste(im)
					im.close()
				elif clipType is Text:
					# TODO: Cache ImageFont
					_font = ImageFont.load_default()

					try:
						_font = ImageFont.load(clip.font)
					except:
						_font = ImageFont.truetype(clip.font, size=clip.fontsize)

					ctx.text(clip.position, clip.text, fill=clip.color, font=_font)
			#frame.save(f"{self.TMP_FOLDER}-img-seq/{frameIndex}.png", format="PNG")
			avframe = av.VideoFrame.from_image(frame)
			frame.close()

			for packet in stream.encode(avframe):
				container.mux(packet)

			frameIndex += 1
			yield frameIndex - 1

		for packet in stream.encode():
			container.mux(packet)

		container.close()

