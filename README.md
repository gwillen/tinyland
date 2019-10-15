# Tinyland
A very small version of Dynamicland. [For more...](https://www.notion.so/Tinyland-f05733c9b73141c181352f5b5012ce1a)

## Setup
Install dependencies with `pip3 install -r requirements.txt`.

Create a file named "config.toml" at the root directory of the project. See "config-sample.toml" for guidance on what should go in that file.

### Developing offline
You don't have to be connected to a projector and camera to work on Tinyland. You can use a video of Tinycam footage to stand in for real-world user input. Here's a good starting point for this workflow:

```
USE_CAMERA = false 
VIDEO_FILE_PATH = "/path/to/a/video/of/the/table.m4v"
FLIP_PROJECTION = false
``` 

Where can I get some of these test videos? [Right here](https://www.dropbox.com/s/qy7gj1giyj1gpd3/tinyland-test-videos.zip?dl=0)

### Camera selection
There are two way to select a camera:
1) Set it in config: Create a property in config called `VIDEO_CAPTURE_INDEX`. Set it to the integer index of your camera, e.g. `VIDEO_CAPTURE_INDEX = 1`. This varies by system, so you may have to fiddle with it! 
2) Use the camera selector: If `USE_CAMERA = true` and `VIDEO_CAPTURE_INDEX` is not set, Tinyland will open a camera selection screen. Press "n" and "p" to cycle through cameras. Press "s" to select.

### Renderer selection
The Tinyland library supports rendering your application with different renderer modules, as long as they implement the renderer. Renderer [abstract base class](https://docs.python.org/3/library/abc.html) and follow the naming convention `<your renderer name>_renderer.Renderer`. Choose the renderer by setting `RENDERER = <your renderer name>` in your config file. 

For example, to choose the cv2_renderer module, put `RENDERER = "CV2"` in your config. Or, to use the text-only debug renderer, use `RENDERER = "debug"`.

## Usage
`python3 ./tinyland.py`

Two windows will open, "Tinyland" and "Tinycam". Move Tinyland to the projector. Then press "f" to make it fullscreen. (You can also resize it using the ordinary OS window controls.)

Press "c" to run the auto configuration.

Press "q" to quit.
