# VComp
Video compiler framework

## Getting started
```python
from vcompy import Video, Text, Compiler

FPS = 60
VIDEO_SIZE = (1280, 720)

vid = Video.from_file("/path/to/file.mp4")
text = Text("Hey, this thing is working!", font="/path/to/font", fontsize=16, duration=(2 * FPS), position=(0, 0))

compiler = Compiler.simple([vid, tex])
compiler.duration = 2 * FPS
compiler.fps = FPS
compiler.size = VIDEO_SIZE

for progress in compiler.save_as("output.mp4"):
	print(f"{progress}/{compiler.get_duration()}", end='\r')

print()
```
