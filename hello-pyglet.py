import pyglet


circle_locations = ()
window = pyglet.window.Window(fullscreen = True)
stringy = ""
label = pyglet.text.Label(stringy,
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

@window.event
def on_key_press(symbol, modifiers):
  global label, stringy
  stringy  += (chr(symbol))
  label = pyglet.text.Label(stringy,
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')
  print(symbol)

@window.event
def on_mouse_motion(x, y, dx, dy):
  global circle_locations
  circle_locations = circle_locations + (int(x- dx), int(y - dy), int(x), int(y))

@window.event
def on_draw():
  global circle_locations
  window.clear()
  # c = (item for item in circle_locations)
  print("testing start")
  # print(c)
  print("testing end")
  if len(circle_locations) >= 4:
    pyglet.graphics.draw(int(len(circle_locations)/2), pyglet.gl.GL_LINES,
    ('v2i', circle_locations))
  
  label.draw()

pyglet.app.run()