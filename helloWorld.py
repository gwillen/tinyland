def main(snap, ctx):
  # Draw shapes to context based on data in snapshot
  for id, markers in snap.markers.items():
    for marker in markers:
      ctx.rect(marker.center.x, marker.center.y, 150, 150)
      ctx.text(marker.center.x, marker.center.y + 160, str(marker.id))