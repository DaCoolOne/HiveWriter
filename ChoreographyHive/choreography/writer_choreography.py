import math

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator, BallState
from rlbot.utils.structures.game_interface import GameInterface

from choreography.choreography import Choreography
from choreography.drone import slow_to_pos
from choreography.group_step import *
from choreography.dacoolutils import Car_Target, Vec3, clamp

class WriterChoreography(Choreography):
    """
    This was used to create https://www.youtube.com/watch?v=7D5QJipyTrw
    """

    def __init__(self, game_interface: GameInterface):
        super().__init__()
        self.game_interface = game_interface

    def generate_sequence(self):
        self.sequence.clear()

        pause_time = 1.5

        # self.sequence.append(DroneListStep(self.line_up))
        # self.sequence.append(BlindBehaviorStep(SimpleControllerState(), pause_time))
        # self.sequence.append(DroneListStep(self.line_up))
        # self.sequence.append(BlindBehaviorStep(SimpleControllerState(), pause_time))
        # self.sequence.append(DroneListStep(self.place_near_ceiling))
        # self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 0.1))
        # self.sequence.append(PerDroneStep(self.drift_downward, 20))
        # self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 0.5))
        # self.sequence.append(PerDroneStep(self.wave_jump, 10))
        # self.sequence.append(DroneListStep(self.circular_procession))

        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 500], [300, 300, 300], "ABCDEFGH", 18))

        # Testing
        # Teleport outside of map.
        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 500], [300, 300, 300], "", 1))

        self.sequence.append(DroneListStep(self.hide_ball))
        self.sequence.append(DroneFlyStep(self.spinning_cars, 100, 1))


        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 500], [300, 300, 300], "", 17))


        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "I dont", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [900, 0, 1000], [300, 300, 300], "want to", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 500], [300, 300, 300], "feel this", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1200, 0, 500], [500, 500, 500], "way", 1.5))

        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "but its", 0.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1100, 0, 500], [300, 300, 300], "not that", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1200, 0, 800], [500, 500, 500], "easy", 1.5)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 1000], [300, 300, 300], "Complicating", 2))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1100, 0, 500], [300, 300, 300], "things for", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1400, 0, 500], [500, 500, 500], "me", 1.5))
        
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "no its", 0.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1100, 0, 500], [300, 300, 300], "not that", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1200, 0, 800], [500, 500, 500], "easy", 1.5))

        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 1000], [300, 300, 300], "Maybe just a", 1)) # 8
        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 500], [300, 300, 300], "little time", 1.5))
        
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1200, 0, 1000], [300, 300, 300], "can heal me", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1600, 0, 1000], [300, 300, 300], "but it", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1500, 0, 500], [300, 300, 300], "doesnt feel the", 1.5))

        # self.sequence.append(DroneWriteStep(self.game_interface, [1500, 0, 500], [500, 500, 500], "way", 1.5))

        # self.sequence.append(DroneWriteStep(self.game_interface, [0, 0, 1000], [300, 300, 300], "what are you", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 500], [300, 300, 300], "doing to", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], "me", 2)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], " ", 4)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "Watch you", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1300, 0, 500], [300, 300, 300], "break my", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1300, 0, 500], [500, 500, 500], "heart", 3))

        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], " ", 1.5)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "Left me", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1150, 0, 500], [300, 300, 300], "in the", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1200, 0, 500], [500, 500, 500], "dark", 3))

        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], " ", 1.5)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "why did you", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1150, 0, 500], [300, 300, 300], "have to", 1.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1200, 0, 500], [500, 500, 500], "go", 3))

        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], " ", 2)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 1000], [300, 300, 300], "I dont", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [900, 0, 1000], [300, 300, 300], "want to", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [-1000, 0, 500], [300, 300, 300], "feel this", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [1500, 0, 500], [500, 500, 500], "way", 3))

        # self.sequence.append(DroneWriteStep(self.game_interface, [1000, 0, 800], [500, 500, 500], " ", 1)) # 8

        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Though", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Im", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Broken", 2))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Im", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "still", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "hoping", 2))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "I", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "could", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "be", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "with", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "you", 4))

        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "", 0.5))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Im still", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Breathing", 2))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Its", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "not", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "easy", 2))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Im", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "just", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "a", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "fool", 3))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "for", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "you", 2))

        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "", 23))

        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "Im", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "just", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [600, 600, 600], "a", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "fool", 3))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "for", 1))
        # self.sequence.append(DroneWriteStep(self.game_interface, [00, 0, 500], [800, 800, 800], "you", 2))


    def spinning_cars(self, drones, time):
        num_cars_a_ring = 4
        num_cars_b_ring = 8
        num_cars_c_ring = 12

        theta = time * 0.2

        height = clamp((time - 10) * 20, -100, 500)
        width = max(1, 1 + (10 - time) * 0.05)

        spacing_a = math.pi * 2 / num_cars_a_ring
        spacing_b = math.pi * 2 / num_cars_b_ring
        spacing_c = math.pi * 2 / num_cars_c_ring

        r_list = []
        for i in range(num_cars_a_ring):
            a = i * spacing_a + theta
            r_list.append(Car_Target(Vec3(0, 0, 1000 + height) + Vec3(math.sin(a) * 65, math.cos(a) * 65) * width, Vec3(math.sin(a), math.cos(a))))
        
        for i in range(num_cars_b_ring):
            a = i * spacing_b - theta
            r_list.append(Car_Target(Vec3(0, 0, 850 + height) + Vec3(math.sin(a) * 200, math.cos(a) * 200, math.cos(a + theta * 10) * 25) * width, Vec3(math.sin(a), math.cos(a))))
        
        for i in range(num_cars_c_ring):
            a = i * spacing_c + theta
            r_list.append(Car_Target(Vec3(0, 0, 700 + height) + Vec3(math.sin(a) * 300, math.cos(a) * 300, math.cos(a - theta * 10) * 50) * width, Vec3(math.sin(a), math.cos(a))))
        return r_list

    def wave_jump(self, packet, drone, start_time) -> StepResult:
        """
        Makes all cars jump in sequence, "doing the wave" if they happen to be lined up.
        https://gfycat.com/remorsefulsillyichthyosaurs
        """
        elapsed = packet.game_info.seconds_elapsed - start_time
        jump_start = drone.index * 0.06
        jump_end = jump_start + .5
        drone.ctrl = SimpleControllerState(jump=jump_start < elapsed < jump_end)
        wheel_contact = packet.game_cars[drone.index].has_wheel_contact
        return StepResult(finished=elapsed > jump_end and wheel_contact)

    def circular_procession(self, packet, drones, start_time) -> StepResult:
        """
        Makes all cars drive in a slowly shrinking circle.
        https://gfycat.com/yearlygreathermitcrab
        """
        radian_spacing = 2 * math.pi / len(drones)
        elapsed = packet.game_info.seconds_elapsed - start_time
        radius = 4000 - elapsed * 100
        for i, drone in enumerate(drones):
            progress = i * radian_spacing + elapsed * .5
            target = [radius * math.sin(progress), radius * math.cos(progress), 0]
            slow_to_pos(drone, target)
        return StepResult(finished=radius < 10)

    def line_up(self, packet, drones, start_time) -> StepResult:
        """
        Puts all the cars in a tidy line, very close together.
        """
        start_x = -2000
        y_increment = 100
        start_y = -len(drones) * y_increment / 2
        start_z = 40
        car_states = {}
        for drone in drones:
            car_states[drone.index] = CarState(
                Physics(location=Vector3(start_x, start_y + drone.index * y_increment, start_z),
                        velocity=Vector3(0, 0, 0),
                        rotation=Rotator(0, 0, 0)))
        self.game_interface.set_game_state(GameState(cars=car_states))
        return StepResult(finished=True)

    def place_near_ceiling(self, packet, drones, start_time, beat) -> StepResult:
        """
        Puts all the cars in a tidy line close to the ceiling.
        """
        start_x = 6500
        y_increment = 100
        start_y = -len(drones) * y_increment / 2
        start_z = 1500
        car_states = {}
        for drone in drones:
            car_states[drone.index] = CarState(
                Physics(location=Vector3(start_y + drone.index * y_increment, start_x, start_z),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0),
                        rotation=Rotator(math.pi * 1, 0, 0)))
        self.game_interface.set_game_state(GameState(cars=car_states))
        return StepResult(finished=packet.game_info.seconds_elapsed-start_time>0.2)

    def drift_downward(self, packet, drone, start_time) -> StepResult:
        """
        Causes cars to boost and pitch until they land on their wheels. This is tuned to work well when
        place_near_ceiling has just been called.
        """
        drone.ctrl = SimpleControllerState(boost=drone.vel[2] < -280, throttle=1, pitch=-0.15)
        wheel_contact = packet.game_cars[drone.index].has_wheel_contact
        return StepResult(finished=wheel_contact)

    def hide_ball(self, packet, drones, start_time, beat) -> StepResult:
        """
        Places the ball above the roof of the arena to keep it out of the way.
        """
        self.game_interface.set_game_state(GameState(ball=BallState(physics=Physics(
            location=Vector3(0, 0, 1500),
            velocity=Vector3(0, 0, 0),
            angular_velocity=Vector3(0, 0, 0)))))
        return StepResult(finished=True)
