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

    def update(self, a, b):
        new_state = (a, b)
        direction = TRANSITIONS.get((self.state, new_state))

        if direction is None:
            return 0

        self.state = new_state

        return direction
                




