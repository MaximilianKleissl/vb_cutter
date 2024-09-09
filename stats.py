class Stats:
  def __init__(self, markers):
    self.markers = markers
    self.validate()

  def validate(self):
    rally_markers = [m[0] for m in self.markers if m[0] in ("W", "G", "B")]
    assert len(rally_markers) % 2 == 0
   
    assert not "B" in rally_markers[1::2]
    assert not "G" in rally_markers[::2]
    assert not "W" in rally_markers[::2]