import os
import sys

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

		# resource cache
		self.pagelifetime = 2 * self.fps
		self.pagesize = 2 * self.fps
		self.pagecache = []

		self.frameIndex = 0

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
		self.frameIndex = 0
		container = av.open(filename, mode='w')
		stream = container.add_stream("mpeg4", rate=self.fps)
		stream.width = self.size[0]
		stream.height = self.size[1]
		stream.pix_fmt = "yuv420p"

		# Set container flags
		container.flush_packets = True
		# TODO: container.format.allow_flush = True

		try:
			os.mkdir(f"{self.TMP_FOLDER}-img-seq/")
		except:
			pass

		# Last frame where?
		duration = self.get_duration()
		while self.frameIndex < duration:
			frame = Image.new("RGB", self.size, (0, 0, 0))
			ctx = ImageDraw.Draw(frame)
			clipsInFrame = self.get_clips_in_frame(self.frameIndex)
			newCache = []

			for clip in clipsInFrame:
				clipType = type(clip)

				# Check if clip not yet in cache
				# then sign
				notcached = False
				if not clip in self.pagecache:
					notcached = True

				# Video is base media, so they have (0, 0) position
				if clipType is Video:
#					print(f"[{self.frameIndex}], Cached: {not notcached}")
					if notcached:
						# Create subclip
						csstart = clip.clip_start
						cstart = clip.start
						csend = cstart + self.pagelifetime #clip.duration
						subclip = clip.sub_clip_copy(csstart, csend, True, start=(cstart))

						# Append to cache
						self.pagecache.append(subclip)
						newCache.append(subclip)
						# Append to clips
						self.clips.append(subclip)

						# Remove part of original
						clip.start = subclip.start + subclip.duration
						clip.duration -= subclip.duration
						clip.sub_clip(csend, cacheframes=False)

						# Overwrite clip
						clip = subclip
#						print(f"{clip.clip_start} <{clip.start}>---------<{clip.start + clip.duration}>")

					# Paste video into canvas
					im = clip.get_frame_pil(self.frameIndex - clip.start)
					if not im is None:
						frame.paste(im)
						im.close()
				elif clipType is Text:
					# TODO: Cache ImageFont
					_font = ImageFont.load_default()

					try:
						_font = ImageFont.load(clip.font)
					except:
						_font = ImageFont.truetype(clip.font, size=clip.fontsize)

					ctx.text(
						clip.position, clip.text,
						fill=clip.color, font=_font, anchor=clip.anchor, align=clip.align
					)
			#frame.save(f"{self.TMP_FOLDER}-img-seq/{self.frameIndex}.png", format="PNG")
			avframe = av.VideoFrame.from_image(frame)
			frame.close()

			# Check for outdated cache
			for cache in self.pagecache:
				if not cache in clipsInFrame and not cache in newCache:
					self.pagecache.remove(cache)
					self.clips.remove(cache)

			for packet in stream.encode(avframe):
				container.mux(packet)

			self.frameIndex += 1
			yield self.frameIndex - 1

		for packet in stream.encode():
			container.mux(packet)

		container.close()

