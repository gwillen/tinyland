import tinyland
import random
import numpy as np
import context
import time

CONTEXT_WIDTH = 1366 # This stuff should be on the context object,
CONTEXT_HEIGHT = 768
PADDING = 5

NPLANETS = 25
MAX_INITIAL_VELOCITY = 20
G = 10000.
MSTAR = 2.  # MPLANET effectively 0 for now, no planet-planet gravity
MAX_TRAIL = 100

planets = []
stars = []

def init_planet(p):
  px = float(random.randrange(CONTEXT_WIDTH))
  py = float(random.randrange(CONTEXT_HEIGHT))
  pdx = float(random.randrange(-100.0, 100.0)) / 100.0 * MAX_INITIAL_VELOCITY
  pdy = float(random.randrange(-100.0, 100.0)) / 100.0 * MAX_INITIAL_VELOCITY
  pcolor = (random.randrange(256), random.randrange(256), random.randrange(256))
  p['pos'] = np.array((px, py))
  p['vel'] = np.array((pdx, pdy))
  p['trail'] = []
  p['color'] = pcolor

last_ran = None
def app(snap, ctx):
  global planets, stars
  global last_ran

  now = time.time()
  if last_ran is not None:
    delay = now - last_ran
    print("frame interval: " + str(delay * 1000) + "ms")
  last_ran = now

  stars = []
  for markers in snap.markers.values():
    for marker in markers:
      stars.append({'pos': np.array((marker.center.x, marker.center.y)) })

  for planet in planets:
    # Remove and respawn planets that get too far away from the viewport
    if (planet['pos'][0] < -CONTEXT_WIDTH or
        planet['pos'][0] > 2*CONTEXT_WIDTH or
        planet['pos'][1] < -CONTEXT_HEIGHT or
        planet['pos'][1] > 2*CONTEXT_HEIGHT):
      init_planet(planet)

    for star in stars:
      r = planet['pos'] - star['pos']
      r_sqrd = r.dot(r)
      r_mag = np.sqrt(r_sqrd)
      r_unit = r / r_mag
      # no planet-planet interactions for now, and planet masses / star masses all equal, with planet <<< star
      a = -(float(G * MSTAR) / r_sqrd) * r_unit
      planet['vel'] += a
    planet['trail'].append(planet['pos'].copy())
    if len(planet['trail']) > MAX_TRAIL:
      planet['trail'] = planet['trail'][1:]
    planet['pos'] += planet['vel']
    ctx.circle(planet['pos'][0], planet['pos'][1], 3)
    for pos in planet['trail']:
      ctx.circle(pos[0], pos[1], 1, planet['color'])

  for star in stars:
    ctx.circle(star['pos'][0], star['pos'][1], 75)


if __name__ == "__main__":
  for i in range(NPLANETS):
    planets.append({})
    init_planet(planets[-1])

  tinyland.run(app)
