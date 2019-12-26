from typing import Callable, List

import math

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator, BallState

from choreography.drone import Drone

from choreography.constants import BPM, MPB, Div_60, CHARACTER

from choreography.dacoolutils import Align_Car_Fast, delta_v, Vec3

class StepResult:
	def __init__(self, finished: bool = False):
		self.finished = finished

class GroupStep:
	def perform(self, packet: GameTickPacket, drones: List[Drone]) -> StepResult:
		pass

class DroneListStep(GroupStep):
	"""
	Takes a function that receives the entire drone list. More powerful but less
	convenient than PerDroneStep. It should be possible to accomplish almost anything
	with this one.
	"""
	def __init__(self, fn: Callable[[GameTickPacket, List[Drone], float], StepResult]):
		self.fn = fn
		self.start_time = None
	
	def perform(self, packet, drones):
		if not self.start_time:
			self.start_time = packet.game_info.seconds_elapsed
		return self.fn(packet, drones, self.start_time, (packet.game_info.seconds_elapsed - self.start_time) * Div_60 * BPM)

class DroneWriteStep(GroupStep):
	"""
	Similar to DroneListStep, but this function is specifically focused on writing
	letters with drones.
	"""
	def __init__(self, game_interface, v, scale, s: str, duration: float):
		self.game_interface = game_interface
		self.scale = scale
		self.vector = v
		self.chars = []
		self.frame = []
		for l in s:
			c = l.lower()
			print(c)
			if c in CHARACTER:
				print("exists")
				self.chars.append(CHARACTER.get(c))
			else:
				print("does not exist")
				self.chars.append(CHARACTER[" "])
			self.frame.append(0)
		
		self.start_time = None
		self.duration = duration
		self.do_step = False
		self.first = True

	def perform(self, packet, drones):
		if not self.start_time:
			self.start_time = packet.game_info.seconds_elapsed
		beat = (packet.game_info.seconds_elapsed - self.start_time) * Div_60 * BPM
		car_states = {}
		
		w = self.scale[0] * 0.25
		w2 = self.scale[0] * 0.5
		
		f_l = len(self.frame)
		
		for drone in drones:
			
			i = drone.index
			
			if i < len(self.chars) and len(self.chars[i]) > 1:
				drone.ctrl.boost = not self.first
				
				c = self.chars[i]
				f = self.frame[i]
				
				c_l = len(c)
				
				x = c[f % c_l]
				z = c[(f + 1) % c_l]
				
				offset = i - (len(self.chars) - 1) * 0.5
				car_states[i] = CarState(
					Physics(location=Vector3(self.vector[0] + offset * self.scale[0] - w + w2 * x, self.vector[1], self.vector[2] + self.scale[2] * z),
							velocity=Vector3(0, 0, 0),
							angular_velocity=Vector3(0, 0, 0),
							rotation=Rotator(0, math.pi * -0.5, 0)))
				
				if self.do_step:
					self.frame[i] = (f + 2) % c_l
			else:
				car_states[i] = CarState(
					Physics(location=Vector3(i * 120, 0, 5000),
							velocity=Vector3(0, 0, 0),
							angular_velocity=Vector3(0, 0, 0),
							rotation=Rotator(0, math.pi * -0.5, 0)))
				drone.ctrl.boost = False
			
		
		self.game_interface.set_game_state(GameState(cars=car_states))
		
		self.do_step = not self.do_step
		
		self.first = False
		
		return StepResult(finished = beat >= self.duration)

def get_dv(packet, drone, drone_pos, t):
	for i in range(50):
		dv = delta_v(packet, drone, drone_pos, t + i * 0.1)
		if dv.length() < 1066:
			break
	return dv

class DroneFlyStep(GroupStep):
	def __init__(self, fly_pattern: Callable[[List, float], List], max_duration: float, path_strictness: float):
		self.fly_pattern = fly_pattern
		self.max_duration = max_duration
		self.path_strictness = path_strictness
		self.start_time = 0
	
	def perform(self, packet, drones):
		if not self.start_time:
			self.start_time = packet.game_info.seconds_elapsed
		
		fly_pattern = self.fly_pattern(drones, packet.game_info.seconds_elapsed - self.start_time)
		
		for i, drone_pos in enumerate(fly_pattern):
			drone = drones[i]
			if not drone:
				break
			dv = get_dv(packet, drone, drone_pos, self.path_strictness)
			Align_Car_Fast(drone, dv, Vec3(0, 0, 1))
			drone.ctrl.boost = dv.length() > 600
			drone.ctrl.jump = drone.has_wheel_contact
			drone.ctrl.throttle = 1
		
		return StepResult(finished=packet.game_info.seconds_elapsed > self.start_time + self.max_duration)
		
		

class PerDroneStep(GroupStep):
	"""
	Takes a function and applies it to every drone individually. They can still behave differently
	because you have access to the drone's index, position, velocity, etc.
	"""
	def __init__(self, bot_fn: Callable[[GameTickPacket, Drone, float], StepResult], max_duration: float):
		self.bot_fn = bot_fn
		self.max_duration = max_duration
		self.start_time = None

	def perform(self, packet, drones: List[Drone]):
		if not self.start_time:
			self.start_time = packet.game_info.seconds_elapsed

		if packet.game_info.seconds_elapsed > self.start_time + self.max_duration:
			return StepResult(finished=True)

		finished = True
		for drone in drones:
			result = self.bot_fn(packet, drone, self.start_time)
			finished = not result.finished and finished
		return StepResult(finished=finished)


class BlindBehaviorStep(PerDroneStep):
	"""
	For every drone in the list, output the given controls for the specified duration.
	For example you could make everyone to boost simultaneously for .5 seconds.
	"""
	def __init__(self, controls: SimpleControllerState, duration: float):
		super().__init__(self.blind, duration)
		self.controls = controls

	def blind(self, packet: GameTickPacket, drone: Drone, elapsed: float):
		drone.ctrl = self.controls
		return StepResult(finished=False)

