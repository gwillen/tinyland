# Tinyland
A very small version of Dynamicland. [For more...](https://www.notion.so/Tinyland-f05733c9b73141c181352f5b5012ce1a)

## Setup
Install dependencies with `pip3 install -r requirements.txt`.

Create a file named "config.toml" at the root directory of the project. See "config-sample.toml" for guidance on what should go in that file.

Here's a good starting point for developing offline:
```
USE_CAMERA = false 
VIDEO_FILE_PATH = "/path/to/a/video/of/the/table.m4v"
FLIP_PROJECTION = false
``` 

Where can I get some of these test videos? [Right here](https://www.dropbox.com/s/qy7gj1giyj1gpd3/tinyland-test-videos.zip?dl=0)

## Usage
`python3 ./tinyland.py`

Two windows will open, "Tinyland" and "Tinycam". Move Tinyland to the projector. Then press "f" to make it fullscreen. (You can also resize it using the ordinary OS window controls.)

Press "c" to run the auto configuration.

Press "q" to quit.
