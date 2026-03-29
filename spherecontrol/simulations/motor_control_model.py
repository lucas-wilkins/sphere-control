import numpy as np


class MotorControlModel:
    def __init__(self):
        self.n_steps_per_revolution = 50

        self.target_position = 0
        self.actual_position = 0

        self.moving = False

    def set_target_position(self, target_position):
        """ Set the target position to the shortest way """

        new_actual_position = self.actual_position % self.n_steps_per_revolution

        mid = target_position % self.n_steps_per_revolution
        low = mid - self.n_steps_per_revolution
        hi = mid + self.n_steps_per_revolution

        # Find the smallest relative distance
        low_dist = abs(low - new_actual_position)
        mid_dist = abs(mid - new_actual_position)
        hi_dist = abs(hi - new_actual_position)

        # Fast C-like test
        if low_dist < mid_dist:
            if hi_dist < low_dist:
                target_position = hi
            else:
                target_position = low
        else:
            # low_dist is not the one
            if hi_dist < mid_dist:
                target_position = hi
            else:
                target_position = mid

        self.target_position = target_position
        self.actual_position = new_actual_position
        self.moving = True

    @property
    def position(self):
        return self.actual_position % self.n_steps_per_revolution

    def step(self) -> float | None:
        """ do a step (if not in position) return time between """

        if self.actual_position < self.target_position:
            # Negative step would happen here
            self.actual_position += 1

        elif self.actual_position > self.target_position:
            # Positive step would happen here
            self.actual_position -= 1

        else:
            self.moving = False

if __name__ == "__main__":

    motor_control_model = MotorControlModel()
    n = 50

    rng = np.random.default_rng(100)
    target_positions = rng.integers(0, motor_control_model.n_steps_per_revolution, size=n)

    angle = []
    radius = []
    for i in range(n):
        target_position = int(target_positions[i])
        r = i + 1.0

        angle.append(motor_control_model.position)
        radius.append(r)


        motor_control_model.set_target_position(target_position)

        start = motor_control_model.actual_position

        # print(i, ":", motor_control_model.target_position, motor_control_model.actual_position)

        while motor_control_model.moving:
            motor_control_model.step()

            angle.append(motor_control_model.position)
            radius.append(r)

        end = motor_control_model.actual_position

        print(i, ":", end - start)

    angle = (2*np.pi/motor_control_model.n_steps_per_revolution) * np.array(angle, dtype=float)
    radius = np.array(radius)

    import matplotlib.pyplot as plt

    plt.plot(radius*np.sin(angle), radius*np.cos(angle))

    plt.show()