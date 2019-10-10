import tinyland
import random

CONTEXT_WIDTH = 1366 # This stuff should be on the context object,
CONTEXT_HEIGHT = 768
PADDING = 5

player1 = None
player2 = None
ball = None

class Paddle:
  def __init__(self, x, y, width=40, height=250):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.score = 0

  def updateY(self, marker):
    self.y = marker.center.y
  
  def render(self, ctx):
    ctx.rect(self.x, self.y, self.width, self.height)

class Ball:
  def __init__(self, x, y, vx=15, vy=15, size=40):
    self.x = x
    self.y = y
    self.vx = vx
    self.vy = vy
    self.size = size

  def update(self):
    self.x += self.vx
    self.y += self.vy

  def render(self, ctx):
    ctx.rect(self.x, self.y, self.size, self.size)

def collide_ball():
    if (ball.y >= CONTEXT_HEIGHT - ball.size) or (ball.y <= ball.size): ball.vy = -ball.vy
    for player in [player1, player2]:
      if abs(ball.x - player.x) <= (ball.size / 2) + (player.width / 2) + PADDING:
        if abs(ball.y - player.y) <= (ball.size / 2) + (player.height / 2) + PADDING:
          ball.vx = -ball.vx
    if (ball.x > CONTEXT_WIDTH):
      player1.score += 1
      ball.x = CONTEXT_WIDTH / 2
      ball.y = CONTEXT_HEIGHT / 2
    elif (ball.x < 0):
      player2.score += 1
      ball.x = CONTEXT_WIDTH / 2
      ball.y = CONTEXT_HEIGHT / 2

def app(snap, ctx):
  # Draw shapes to context based on data in snapshot
  collide_ball()

  for markers in snap.markers.values():
    for marker in markers:
      if marker.center.x < CONTEXT_WIDTH / 2:
        player1.updateY(marker)
      else:
        player2.updateY(marker)
  player1.render(ctx)
  player2.render(ctx)

  ball.update()
  ball.render(ctx)

  ctx.text(CONTEXT_WIDTH / 4, CONTEXT_HEIGHT / 4, str(player1.score))
  ctx.text(CONTEXT_WIDTH / 4 * 3, CONTEXT_HEIGHT / 4, str(player2.score))


if __name__ == "__main__":
  player1 = Paddle(200, 10)
  player2 = Paddle(CONTEXT_WIDTH - 200, 10) # Would be nice have access to projector width here :)

  ball_vx = random.choice([15, -15])
  ball_vy = random.choice([15, -15])
  ball = Ball(CONTEXT_WIDTH/2, CONTEXT_HEIGHT/2, ball_vx, ball_vy)

  tinyland.run(app)