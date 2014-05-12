from bisect import insort

class ECDF:
    """
    http://en.wikipedia.org/wiki/ECDF
    """

    def __init__(self, size = 100):
        self.size = size
        self.values = []

    def add(self, number):
        if len(self.values) >= self.size:
            self.shorten()
        index = insort(self.values, number)
            
    def shorten(self):
        for i in range(self.size // 4):
            self.values.pop(i)
            self.values.pop(-i - 1)

    def inverse(self, cumulative_probability):
        assert self.values, "there should be values"
        assert 0 <= cumulative_probability <= 1
        if cumulative_probability == 1:
            index = -1
        else:
            index = int(len(self.values) * cumulative_probability)
        return self.values[index]
