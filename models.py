class NPair:
    def __init__(self, startLocation, endLocation, startTime, endTime):
        self.startLocation = (startLocation["x"], startLocation["y"])
        self.endLocation = (endLocation["x"], endLocation["y"])
        self.startTime = startTime
        self.endTime = endTime
