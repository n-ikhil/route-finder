class NodePoint:
    def __init__(self, location, time="0"):
        self.locationX = location["x"]
        self.locationY = location["y"]
        self.time = time


class NodePair:
    def __init__(self, location, userid, time):
        self.src = NodePoint(location["src"], time["start"])
        self.dst = NodePoint(location["dst"], time["end"])
        self.user = userid
