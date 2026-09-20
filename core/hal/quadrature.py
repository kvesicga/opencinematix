DETENT = 4

TRANSITIONS = {
    ((1, 1), (0, 1)): 1,
    ((0, 1), (0, 0)): 1,
    ((0, 0), (1, 0)): 1,
    ((1, 0), (1, 1)): 1,
    ((1, 1), (1, 0)): -1,
    ((1, 0), (0, 0)): -1,
    ((0, 0), (0, 1)): -1,
    ((0, 1), (1, 1)): -1,
}


class QuadratureDecoder:

    def __init__(self):
        self.state = (1, 1)
        self.steps = 0

    def update(self, a, b):
        new_state = (a, b)
        direction = TRANSITIONS.get((self.state, new_state))

        if direction is None:
            return 0

        self.state = new_state
        self.steps += direction

        if abs(self.steps) < DETENT:
            return 0

        step = 1 if self.steps > 0 else -1
        self.steps = 0

        return step
                




