from typing import Callable, List

import math

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator, BallState

from choreography.drone import Drone

from choreography.constants import BPM, Div_60, CHARACTER

from choreography.dacoolutils import Align_Car_Fast, delta_v, Vec3
from choreography.dacoolutils import Rotator as Rotation

class StepResult:
	def __init__(self, finished: bool = False, execute_time: float = 0):
		self.finished = finished
		self.execute_time = execute_time if finished else 0

class GroupStep:
	def perform(self, packet: GameTickPacket, drones: List[Drone], beat: float) -> StepResult:
		return StepResult()
	def set_start_beat(self, start_beat):
		self.start_beat = start_beat

# Merges two group steps and performs them at the same time. Only one group step needs to terminate.
class MergeStep(GroupStep):
	def __init__(self, merge_list: List[GroupStep], bot_list: List[int]):
		if len(merge_list) != len(bot_list):
			raise ValueError
		self.groups = merge_list
		self.group_counts = bot_list
	
	def set_start_beat(self, start_beat):
		for group in self.groups:
			group.set_start_beat(start_beat)
	
	def perform(self, packet: GameTickPacket, drones: List[Drone], beat: float) -> StepResult:
		finished = False
		finish_duration = 0
		index = 0
		for i, count in enumerate(self.group_counts):
			d = drones[index : index + count]
			o = self.groups[i].perform(packet, d, beat)
			
			index += count
			
			finished = finished or o.finished
			finish_duration = max(finish_duration, o.execute_time)
		
		return StepResult(finished, finish_duration)
		

# Type of step that exectutes a list of steps in sequence.
class SequentialStep(GroupStep):
	def __init__(self, merge_list: List[GroupStep] = []):
		self.groups = merge_list
		self.sum_time = 0
		self.current_index = 0
	def append(self, a: GroupStep):
		self.groups.append(a)
	def set_start_beat(self, start_beat):
		self.start_beat = start_beat
		if len(self.groups) > 0:
			self.groups[0].set_start_beat(self.start_beat + self.sum_time)
		
	def perform(self, packet: GameTickPacket, drones: List[Drone], beat: float) -> StepResult:
		if self.current_index < len(self.groups):
			result = self.groups[self.current_index].perform(packet, drones, beat)
			
			if result.finished:
				self.current_index += 1
				self.sum_time += result.execute_time
				
				if self.current_index < len(self.groups):
					self.groups[self.current_index].set_start_beat(self.start_beat + self.sum_time)
		
		return StepResult(self.current_index >= len(self.groups), self.sum_time)
	

class DroneListStep(GroupStep):
	"""
	Takes a function that receives the entire drone list. More powerful but less
	convenient than PerDroneStep. It should be possible to accomplish almost anything
	with this one.
	"""
	def __init__(self, fn: Callable[[GameTickPacket, List[Drone], float], StepResult]):
		self.fn = fn
		self.start_beat = None
	
	def perform(self, packet, drones, beat):
		return self.fn(packet, drones, self.start_beat, beat)

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
				self.chars.append(CHARACTER.get(c))
			else:
				print(f"Undefined character {c}")
				self.chars.append(CHARACTER[" "])
			self.frame.append(0)
		
		self.start_beat = None
		self.duration = duration
		self.do_step = False
		self.first = True

	def perform(self, packet, drones, beat):
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
		
		return StepResult(beat - self.start_beat >= self.duration, self.duration)

def get_dv(packet, drone, drone_pos, t):
	for i in range(50):
		dv = delta_v(packet, drone, drone_pos, t + i * 0.1)
		if dv.length() < 1066:
			break
	return dv

class DroneFlyStep(GroupStep):
	def __init__(self, fly_pattern: Callable[[List, float], List], duration: float, path_strictness: float):
		self.fly_pattern = fly_pattern
		self.duration = duration
		self.path_strictness = path_strictness
		self.start_beat = None
	
	def perform(self, packet, drones, beat):
		
		fly_pattern = self.fly_pattern(packet, drones, beat - self.start_beat)
		
		for i, drone_pos in enumerate(fly_pattern):
			
			if i >= len(drones):
				print(f"Warning, index {i} does not exist")
				break
			
			drone = drones[i]
			if drone_pos.pos:
				dv = get_dv(packet, drone, drone_pos.pos, self.path_strictness)
				Align_Car_Fast(drone, dv, drone_pos.up)
				drone.ctrl.boost = dv.length() > 600
				drone.ctrl.jump = drone.has_wheel_contact
				drone.ctrl.throttle = 1
			else:
				dv = Vec3(1).align_to(Rotation.cast_np(drone.rot))
				Align_Car_Fast(drone, dv, drone_pos.up)
		
		return StepResult(beat >= self.start_beat + self.duration, self.duration)
		
		

class FireworksStep(GroupStep):
	def __init__(self, game_interface, start_loc, end_loc, end_time, duration):
		self.game_interface = game_interface
		
		self.start_loc = start_loc
		self.end_loc = end_loc
		self.end_time = end_time
		
		self.start_beat = None
		
		self.stage = 0
		
		self.duration = duration
	
	def perform(self, packet, drones, beat):
		current_time = beat - self.start_beat
		
		if self.stage == 0:
			car_states = {}
			
			car_states[drones[0].index] = CarState(
				Physics(location=Vector3(self.start_loc.x, self.start_loc.y, self.start_loc.z),
						velocity=Vector3(0, 0, 300),
						angular_velocity=Vector3(0, 0, 0),
						rotation=Rotator(math.pi * 0.5, 0, 0)))
			
			self.game_interface.set_game_state(GameState(cars=car_states))
			self.stage = 1
		
		if self.stage == 1:
			
			drone = drones[0]
			
			side = Vec3(y=1).align_to(Rotation.cast_np(drone.rot))
			
			dv = get_dv(packet, drone, self.end_loc, 0.1)
			Align_Car_Fast(drone, dv, side)
			drone.ctrl.boost = dv.length() > 600
			drone.ctrl.throttle = 1
			
			if current_time > self.end_time:
				car_states = {}
				
				car_pos = Vec3.cast_np(drone.pos)
				
				for i in range(len(drones)):
					a = (i / len(drones)) * math.pi * 2
					v = Vec3(math.cos(a), math.sin(a)) * 100
					
					car_states[drones[i].index] = CarState(
						Physics(location=Vector3(car_pos.x + v.x, car_pos.y + v.y, car_pos.z),
							velocity=Vector3(0, 0, 700),
							angular_velocity=Vector3(0, 0, 0),
							rotation=Rotator(0.1, a, 0)))
				
				self.game_interface.set_game_state(GameState(cars=car_states))
				
				self.stage = 2
			
		elif self.stage == 2:
			for drone in drones:
				drone.ctrl.boost = True
			
		
		return StepResult(beat >= self.start_beat + self.duration, self.duration)

class PerDroneStep(GroupStep):
	"""
	Takes a function and applies it to every drone individually. They can still behave differently
	because you have access to the drone's index, position, velocity, etc.
	"""
	def __init__(self, bot_fn: Callable[[GameTickPacket, Drone, float], StepResult], duration: float):
		self.bot_fn = bot_fn
		self.duration = duration
		self.start_beat = None

	def perform(self, packet, drones: List[Drone], beat):

		if beat > self.start_beat + self.duration:
			return StepResult(True, self.duration)

		finished = True
		for drone in drones:
			result = self.bot_fn(packet, drone, self.start_beat, beat)
			finished = result.finished and finished
		return StepResult(finished)


class BlindBehaviorStep(PerDroneStep):
	"""
	For every drone in the list, output the given controls for the specified duration.
	For example you could make everyone to boost simultaneously for .5 seconds.
	"""
	def __init__(self, controls: SimpleControllerState, duration: float, exclude=[]):
		super().__init__(self.blind, duration)
		self.controls = controls
		self.duration = duration
		self.exclude = exclude

	def blind(self, packet: GameTickPacket, drone: Drone, start: float, elapsed: float):
		if drone.index in self.exclude:
			return StepResult(False)
		drone.ctrl = self.controls
		return StepResult(False)

