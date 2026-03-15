import numpy as np


class MotorModel:
    def __init__(self,
                 motor_steps_per_revolution: int = 200,
                 driver_microstepping: int = 32,
                 encoder_steps_per_revolution: int = 4096,
                 driver_gear_teeth: int = 16,
                 driven_gear_teeth: int = 80,
                 backlash_deg: float = 0.05,
                 encoder_offset: float = 1234.5,
                 noise_in_encoder_units: float = 0.2):

        self.encoder_offset = encoder_offset
        self.noise_in_encoder_units = noise_in_encoder_units

        # Useful derived quantities

        self.steps_per_revolution = motor_steps_per_revolution * driver_microstepping * \
                                    driven_gear_teeth / driver_gear_teeth

        self.driver_steps_per_encoder_step = self.steps_per_revolution / encoder_steps_per_revolution

        self.backlash_steps = self.steps_per_revolution * backlash_deg / 360


        #print(self.steps_per_revolution, self.driver_steps_per_encoder_step, self.backlash_steps)

        # State variables
        self.commanded_position_steps = 0
        self.backlash_position = 0.0
        self.backlash_effective_position = 0.0

    def move_steps(self, n_steps: int):

        # How many of these steps go into the backlash, how many move the output
        if n_steps > 0:

            # Should be a number from 0 to 2*backlash_steps
            available_backlash_steps = self.backlash_steps - self.backlash_position

            if n_steps > available_backlash_steps:
                self.backlash_position = self.backlash_steps
                self.backlash_effective_position += n_steps - available_backlash_steps
            else:
                self.backlash_position += n_steps

        else:
            available_backlash_steps = -self.backlash_steps - self.backlash_position

            if n_steps < available_backlash_steps:
                self.backlash_position = -self.backlash_steps
                self.backlash_effective_position += n_steps - available_backlash_steps
            else:
                self.backlash_position += n_steps

        # Update current step position
        self.commanded_position_steps += n_steps


    def get_encoded_position(self):
        return round(self.encoder_offset + self.backlash_effective_position / self.driver_steps_per_encoder_step
                     + self.noise_in_encoder_units * (np.random.rand() - 0.5))

    def move_to_encoder_position(self, target_encoder_position):
        current_position = self.get_encoded_position()
        steps = (target_encoder_position - current_position) * self.driver_steps_per_encoder_step
        self.move_steps(steps)

def backlash_test_1():
    motor = MotorModel()

    n = 15

    steps = ([1 for _ in range(n)] + [-1 for _ in range(n)])*3

    step_position = [motor.commanded_position_steps]
    backlash = [motor.backlash_position]
    including_backlash = [motor.backlash_effective_position]
    for step in steps:
        motor.move_steps(step)

        step_position.append(motor.commanded_position_steps)
        backlash.append(motor.backlash_position)
        including_backlash.append(motor.backlash_effective_position)

    import matplotlib.pyplot as plt
    plt.plot(step_position)
    plt.plot(backlash)
    plt.plot(including_backlash)

    plt.show()

def backlash_test_1():
    motor = MotorModel()

    n = 15

    steps = ([1 for _ in range(n)] + [-1 for _ in range(n)])*3

    step_position = [motor.commanded_position_steps]
    backlash = [motor.backlash_position]
    including_backlash = [motor.backlash_effective_position]

    for step in steps:
        motor.move_steps(step)

        step_position.append(motor.commanded_position_steps)
        backlash.append(motor.backlash_position)
        including_backlash.append(motor.backlash_effective_position)

    import matplotlib.pyplot as plt
    plt.plot(step_position)
    plt.plot(backlash)
    plt.plot(including_backlash)

    plt.show()




if __name__ == "__main__":
    backlash_test_1()