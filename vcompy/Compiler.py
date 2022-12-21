6from PIL import Image, ImageDraw, ImageFont

from .Video import Video

class Compiler:
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
			if clip.start >= i and i <= clip.start + clip.duration:
				clips.append(clip)

		return clips

	def save_as(self, filename):
		frameIndex = 0

		# Last frame where?
		duration = self.get_duration()
		while frameIndex < duration:
			frame = Image.new("RGB", self.size, (0, 0, 0))
			ctx = ImageDraw.Draw(frame)
			for clip in self.get_clips_in_frame(frameIndex):
				if clip is Video:
					im = clip.get_frame_pil() # includes .resize
					frame.paste(im, clip.position)
