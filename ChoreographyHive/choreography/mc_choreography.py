import math
import random
import time

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.game_state_util import GameState, CarState, Physics, Vector3, Rotator, BallState
from rlbot.utils.structures.game_interface import GameInterface

from choreography.choreography import Choreography
from choreography.drone import slow_to_pos
from choreography.group_step import *
from choreography.dacoolutils import Car_Target, Vec3, clamp
from choreography.dacoolutils import Rotator as Rotation

file_name = "audio_chop.mp3"

import pygame as pg
def stop_music():
	pg.mixer.music.fadeout(1000)
def play_music(music_file, volume=0.8):
	'''
	stream music with mixer.music module in a blocking manner
	this will stream the sound from disk while playing
	'''
	# set up the mixer
	freq = 24000     # audio CD quality
	freq = 48000     # audio CD quality
	bitsize = -16    # unsigned 16 bit
	channels = 2     # 1 is mono, 2 is stereo
	buffer = 4096    # number of samples (experiment to get best sound)
	pg.mixer.init(freq, bitsize, channels, buffer)
	# volume value 0.0 to 1.0
	pg.mixer.music.set_volume(volume)
	clock = pg.time.Clock()
	try:
		pg.mixer.music.load(music_file)
		pg.mixer.music.play()
		while pg.mixer.music.get_pos() < 100: # Ensure that the song has indeed loaded and is playing.
			clock.tick(100)
		print("Music file {} loaded!".format(music_file))
	except pg.error:
		print("File {} not found! ({})".format(music_file, pg.get_error()))
		return
	
	print(pg.mixer.music.get_pos() / 1000)
	return pg.mixer.music.get_pos() / 1000
	# while pg.mixer.music.get_busy():
		# check if playback has finished
		# clock.tick(30)

def invert_list(n, a, b):
	a2 = []
	first_index = min(a, b)
	for i in range(abs(b - a)):
		if not i + first_index in n:
			a2.append(i + first_index)
	return a2

y_offset_mc = 0
background_dancers = 8

class WriterChoreography(Choreography):

	def __init__(self, game_interface: GameInterface):
		super().__init__()
		self.game_interface = game_interface

	def generate_sequence(self):
		self.sequence.clear()

		pause_time = 2

		# self.sequence.append(DroneListStep(self.line_up))
		self.sequence.append(BlindBehaviorStep(SimpleControllerState(), pause_time))
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

		# self.sequence.append(DroneFlyStep(self.experimental_formation, 100, 1))

		# self.sequence.append(DroneListStep(self.start_playing_music))
		
		# self.sequence.append(DroneListStep(self.initial_setup))
		# self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 0.05))
		# self.sequence.append(BlindBehaviorStep(SimpleControllerState(jump=True, pitch=1), 0.2))
		# self.sequence.append(DroneFlyStep(self.fly_up_to_ball, 2.75, 1))
		# self.sequence.append(DroneListStep(self.zero_velocity))
		# self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 4))
		
		# A quick way of spawning all the cars.
		self.sequence.append(DroneListStep(self.make_sure_all_cars_spawn))
		self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 8))
		self.sequence.append(DroneListStep(self.hide_ball))
		
		# self.sequence.append(DroneFlyStep(self.spinning_cars_2, 80, 1))
		
		# self.sequence.append(DroneListStep(self.two_car_setup))
		
		self.sequence.append(DroneListStep(self.setup_ball))
		self.sequence.append(DroneListStep(self.teleport_cars_away))
		self.sequence.append(MergeStep([
			DroneFlyStep(self.spinning_cars_3, 90, 1),
			SequentialStep([BlindBehaviorStep(SimpleControllerState(), 80), FireworksStep(self.game_interface, Vec3(1000, -3500, 100), Vec3(2000, -3500, 2400), 3, 16)]),
			SequentialStep([BlindBehaviorStep(SimpleControllerState(), 80), FireworksStep(self.game_interface, Vec3(-1000, -3500, 100), Vec3(-2000, -3500, 2400), 3, 16)]),
			SequentialStep([BlindBehaviorStep(SimpleControllerState(), 80), FireworksStep(self.game_interface, Vec3(500, -3500, 100), Vec3(1000, -3500, 2400), 3, 16)]),
			SequentialStep([BlindBehaviorStep(SimpleControllerState(), 80), FireworksStep(self.game_interface, Vec3(-500, -3500, 100), Vec3(-1000, -3500, 2400), 3, 16)])
		],
		[4, 8, 8, 8, 8]))
		
		# self.sequence.append(MergeStep([
			# GroupStep(),
			# DroneListStep(self.place_near_ceiling),
			# DroneListStep(self.teleport_cars_away),
		# ], [4, 8, 52]))
		# self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 1))
		# self.sequence.append(DroneListStep(self.place_first_four))
		# self.sequence.append(DroneListStep(self.start_playing_music))
		# self.sequence.append(BlindBehaviorStep(SimpleControllerState(), 7.8))
		
		# jump_bots = SequentialStep()
		# for i in range(16):
			# a = i % 4
			# l = []
			# Ignore the first four bots, since those bots are going to be doing other things.
			# for i in range(4, background_dancers + 4, 4):
				# l.append(i + a)
			# bot_exclude_list = invert_list(l, 0, 4 + background_dancers)
			# jump_bots.append(BlindBehaviorStep(SimpleControllerState(jump = True), 0.2, bot_exclude_list))
			# jump_bots.append(BlindBehaviorStep(SimpleControllerState(), 0.8))
		# for i in range(32):
			# a = i % 4
			# l = []
			# Ignore the first four bots, since those bots are going to be doing other things.
			# for i in range(4, background_dancers + 4, 4):
				# l.append(i + a)
			# bot_exclude_list = invert_list(l, 0, 4 + background_dancers)
			# jump_bots.append(BlindBehaviorStep(SimpleControllerState(jump = True), 0.2, bot_exclude_list))
			# jump_bots.append(BlindBehaviorStep(SimpleControllerState(), 0.3))
		
		# jump_bots.append(GroupStep()) # Simple way to make the jump_bots not terminate
		
		# self.sequence.append(MergeStep([
			# SequentialStep([BlindBehaviorStep(SimpleControllerState(), 28), DroneListStep(self.demo_mc), BlindBehaviorStep(SimpleControllerState(), 0.1), DroneListStep(self.replace_mc), BlindBehaviorStep(SimpleControllerState(), 7.9)]), # [BlindBehaviorStep(SimpleControllerState(throttle = 1), 2), DroneFlyStep(self.spinning_cars, 100, 1)]),
			# jump_bots,
			# SequentialStep([
				# BlindBehaviorStep(SimpleControllerState(), 24),
				# FireworksStep(self.game_interface, Vec3(-1000, -1000, 100), Vec3(-1500, -1000, 2500), 4, 16),
			# ]),
			# SequentialStep([
				# BlindBehaviorStep(SimpleControllerState(), 24),
				# FireworksStep(self.game_interface, Vec3(1000, -1000, 100), Vec3(1500, -1000, 2500), 4, 16),
			# ]),
			# SequentialStep([
				# BlindBehaviorStep(SimpleControllerState(), 24),
				# FireworksStep(self.game_interface, Vec3(-500, -1000, 300), Vec3(-1000, -1000, 2500), 4, 16),
			# ]),
			# SequentialStep([
				# BlindBehaviorStep(SimpleControllerState(), 24),
				# FireworksStep(self.game_interface, Vec3(500, -1000, 300), Vec3(1000, -1000, 2500), 4, 16),
			# ]),
		# ], [4, 8, 8, 8, 8, 8]))
		
		# self.sequence.append(DroneListStep(self.end_music))
		

	def spinning_cars_2(self, packet, drones, time):
		num_cars_a_ring = 4
		num_cars_b_ring = 8
		num_cars_c_ring = 12
		num_cars_d_ring = 16

		theta = time * 0.2

		height = 0 # clamp((time - 10) * 20, -100, 500)
		width = max(1, 1 + (10 - time) * 0.05)

		spacing_a = math.pi * 2 / num_cars_a_ring
		spacing_b = math.pi * 2 / num_cars_b_ring
		spacing_c = math.pi * 2 / num_cars_c_ring
		spacing_d = math.pi * 2 / num_cars_d_ring

		r_list = []
		
		r_list.append(Car_Target(Vec3(0, 0, 1150 + height), Vec3(math.sin(-theta), math.cos(-theta))))
		
		for i in range(num_cars_a_ring):
			a = i * spacing_a + theta
			r_list.append(Car_Target(Vec3(0, 0, 1000 + height) + Vec3(math.sin(a) * 100, math.cos(a) * 100) * width, Vec3(math.sin(a), math.cos(a))))
		
		for i in range(num_cars_b_ring):
			a = i * spacing_b - theta
			r_list.append(Car_Target(Vec3(0, 0, 850 + height) + Vec3(math.sin(a) * 200, math.cos(a) * 200, math.cos(a + theta * 10) * 25) * width, Vec3(math.sin(a), math.cos(a))))
		
		for i in range(num_cars_c_ring):
			a = i * spacing_c + theta
			r_list.append(Car_Target(Vec3(0, 0, 700 + height) + Vec3(math.sin(a) * 300, math.cos(a) * 300, math.cos(a - theta * 10) * 50) * width, Vec3(math.sin(a), math.cos(a))))
		
		for i in range(num_cars_d_ring):
			a = i * spacing_d - theta
			r_list.append(Car_Target(Vec3(0, 0, 550 + height) + Vec3(math.sin(a) * 400, math.cos(a) * 400, math.cos(a + theta * 10) * 75) * width, Vec3(math.sin(a), math.cos(a))))
		
		return r_list

	def circular_procession(self, packet, drones, start_beat, beat) -> StepResult:
		"""
		Makes all cars drive in a slowly shrinking circle.
		https://gfycat.com/yearlygreathermitcrab
		"""
		radian_spacing = 2 * math.pi / len(drones)
		elapsed = beat - start_beat
		radius = 3000
		for i, drone in enumerate(drones):
			progress = i * radian_spacing + elapsed * .15
			target = [radius * math.sin(progress), radius * math.cos(progress), 0]
			slow_to_pos(drone, target)
		return StepResult(finished=beat-start_beat>25)

	def drive_to_start_positions(self, packet, drones, start_beat, beat) -> StepResult:
		radian_spacing = 2 * math.pi / (len(drones) - 1)
		elapsed = beat - start_beat
		radius = 3000 - elapsed * 100
		for i, drone in enumerate(drones):
			if i:
				progress = i * radian_spacing
				target = [radius * math.sin(progress), radius * math.cos(progress), 0]
				slow_to_pos(drone, target)
			else:
				slow_to_pos(drone, [0, 0, 0])
		return StepResult(radius<500,elapsed)
	
	def wait_then_drive_away(self, packet, drones, start_beat, beat) -> StepResult:
		
		elapsed = beat - start_beat
		pos = [4000, 4000, 0] if elapsed > 30 else [0, 0, 0]
		
		slow_to_pos(drones[0], pos)
		
		return StepResult(False)
		
	
	def air_dribble_thing(self, packet, drones, time):
		
		ball = packet.game_ball.physics
		
		spin = time * 5
		
		return [
			Car_Target((Vec3.cast(ball.location) + Vec3.cast(ball.velocity)).flatten() + Vec3(z=1000), Vec3(math.sin(spin), math.cos(spin), 0))
		]
		
	
	def two_car_spin(self, packet, drones, time):
		max_radius = 4000
		
		scale = 100
		
		t = abs(max_radius / scale - max(0, time - 10))
		
		v1 = 1300 / scale
		
		theta = v1 * (math.log(t) - 1)
		
		radius = t * scale
		
		r_list = []
		
		for i in range(2):
			a = i * math.pi - theta
			v = Vec3(math.sin(a), math.cos(a))
			r_list.append(Car_Target(Vec3(z=500) + v * radius, Vec3.cast_np(drones[i].pos)))
		
		return r_list

	def fly_up_to_ball(self, packet, drones, time):
		r_list = []
		
		if time < 2:
			r_list.append(Car_Target(
				Vec3(0, 50, 1100)
			))
		else:
			r_list.append(Car_Target(
				up = Vec3(0, 0, -1)
			))
		
		return r_list

	def spinning_cars(self, packet, drones, time):
		num_cars_a_ring = 4
		
		theta = time * 0.15
		
		width = max(1, 1 + (20 - time) * 0.05)
		
		circle_radius = clamp((time - 30) * 100, 0, 1200)
		height = clamp((time - 10) * 20, -100, 500) - clamp(circle_radius, 0, 600)
		
		spacing_a = math.pi * 2 / num_cars_a_ring
		
		r_list = []
		
		for i in range(num_cars_a_ring):
			a = i * spacing_a - theta
			r_list.append(Car_Target(Vec3(0, 0, 500 + height) + Vec3(math.sin(a) * 60, math.cos(a) * 60) * width + Vec3(math.sin(theta) * circle_radius, math.cos(theta) * circle_radius), Vec3(math.sin(a), math.cos(a))))
		
		return r_list

	def spinning_cars_3(self, packet, drones, time):
		num_cars_a_ring = 4
		
		theta = time * 0.15
		
		width = max(1, 1 + (20 - time) * 0.05)
		
		circle_radius = clamp((time - 30) * 100, 0, 6000)
		height = clamp((time - 10) * 20, -100, 500) - clamp(circle_radius, 0, 800)
		
		spacing_a = math.pi * 2 / num_cars_a_ring
		
		r_list = []
		
		for i in range(num_cars_a_ring):
			a = i * spacing_a - theta
			r_list.append(Car_Target(Vec3(0, 0, 500 + height) + Vec3(math.sin(a) * 60, math.cos(a) * 60) * width + Vec3(math.sin(theta), math.cos(theta)) + Vec3(y=-1) * circle_radius, Vec3(math.sin(a), math.cos(a))))
		
		return r_list

	def experimental_formation(self, packet, drones, time):
		num_cars = 12
		spacing_cars = math.pi * 2 / num_cars
		
		theta = time * 0.2
		
		ring_angle = math.pi * 0.15
		rot1 = Rotation(yaw = theta, pitch = ring_angle)
		rot2 = Rotation(yaw = theta, pitch = -ring_angle)
		
		r = []
		for i in range(num_cars):
			d = drones[i]
			a = i * spacing_cars - theta * 2
			r.append(Car_Target(Vec3(0, 0, 700) + Vec3(math.sin(a), math.cos(a)).align_to(rot1) * 500, Vec3.cast_np(d.pos)))
		for i in range(num_cars):
			d = drones[i+num_cars]
			a = i * spacing_cars + spacing_cars * 0.5 - theta * 2
			r.append(Car_Target(Vec3(0, 0, 700) + Vec3(math.sin(a), math.cos(a)).align_to(rot2) * 500, Vec3.cast_np(d.pos)))
		
		return r
		

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

	def start_playing_music(self, packet, drones, start_time, beat) -> StepResult:
		start = time.time()
		t = play_music(file_name, 0.5)
		end = time.time()
		return StepResult(True, -self.to_beats(start - end - t))

	def end_music(self, packet, drones, start_time, beat) -> StepResult:
		stop_music()
		return StepResult(True)

	def teleport_cars_away(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Puts all the cars in a tidy line close to the ceiling.
		"""
		start_x = 0
		x_increment = 130
		y_increment = -10
		y_increment_2 = -200
		
		start_z = 30
		
		car_states = {}
		
		for drone in drones:
			
			if drone.index < 4:
				car_states[drone.index] = CarState(
					Physics(location=Vector3(0, 0, 100),
							velocity=Vector3(0, 0, 0),
							angular_velocity=Vector3(0, 0, 0),
							rotation=Rotator(0, math.pi * 0.5, 0)))
			else:
				dir = -1 if drone.index % 4 >= 2 else 1
				car_states[drone.index] = CarState(
					Physics(location=Vector3(3000 * dir, 4000),
							velocity=Vector3(0, 0, 0),
							angular_velocity=Vector3(0, 0, 0),
							rotation=Rotator(0, math.pi * 0.5, 0)))
				
				# This is how we do it
				if drone.index % 16 == 15 or drone.index + 1 >= len(drones):
					self.game_interface.set_game_state(GameState(cars=car_states))
					car_states = {}
		return StepResult(finished=beat - start_time > 0.1)


	def place_near_ceiling(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Puts all the cars in a tidy line close to the ceiling.
		"""
		start_x = 0
		x_increment = 130
		y_increment = -10
		y_increment_2 = -200
		
		start_z = 30
		
		car_states = {}
		
		def get_position(pos, spread):
			# pos is integer from 0 to 3 repesenting the position.
			
			row = pos % 2
			dir = -1 if pos < 2 else 1
			
			return Vector3(x_increment * spread * dir, y_increment * spread + y_increment_2 * row, start_z)
		
		dl = len(drones)
		for i, drone in enumerate(drones):
			a = (i / (dl - 1) * math.pi * 2)
			while a > math.pi:
				a -= math.pi
			car_states[drone.index] = CarState(
				Physics(location=Vector3(-math.cos(a) * 300, -math.sin(a) * 300, 50),
					velocity=Vector3(0, 0, 0),
					angular_velocity=Vector3(0, 0, 0),
					rotation=Rotator(0, a, 0)))
			
			# This is how we do it
			if drone.index % 16 == 15 or drone.index + 1 >= dl:
				self.game_interface.set_game_state(GameState(cars=car_states))
				car_states = {}
		return StepResult(finished=beat - start_time > 0.1)

	def place_first_four(self, packet, drones, start_time, beat) -> StepResult:
		
		def get_position(index):
			if index == 0:
				return Vector3(0, y_offset_mc)
			if index == 1:
				return Vector3(0, 4000)
			if index == 2:
				return Vector3(3000, 4000)
			if index == 3:
				return Vector3(-3000, 4000)
		
		car_states = {}
		
		for i in range(4):
			drone = drones[i]
			car_states[drone.index] = CarState(
				Physics(location=get_position(i),
						velocity=Vector3(0, 0, 0),
						angular_velocity=Vector3(0, 0, 0),
						rotation=Rotator(0, math.pi * 0.5, 0)))
		
		self.game_interface.set_game_state(GameState(cars=car_states))
		return StepResult(finished=beat-start_time>0.1)
	
	def replace_mc(self, packet, drones, start_time, beat) -> StepResult:
		car_states = {}
		car_states[2] = CarState(
			Physics(location=Vector3(2900, 3000),
				velocity=Vector3(0, 2400, 0),
				angular_velocity=Vector3(0, 0, 0),
				rotation=Rotator(0, math.pi * 0.5, 0)))
		
		car_states[1] = CarState(
			Physics(location=Vector3(0, y_offset_mc),
				velocity=Vector3(0, 0, 0),
				angular_velocity=Vector3(0, 0, 0),
				rotation=Rotator(0, math.pi * 0.5, 0)))
		
		self.game_interface.set_game_state(GameState(cars=car_states, console_commands=["Set WorldInfo TimeDilation 0.8"]))
		return StepResult(beat - start_time>0.2, 0)
	
	def demo_mc(self, packet, drones, start_time, beat) -> StepResult:
		car_states = {}
		
		car_states[2] = CarState(
			Physics(location=Vector3(0, y_offset_mc - 150),
				velocity=Vector3(0, 2400, 0),
				angular_velocity=Vector3(0, 0, 0),
				rotation=Rotator(0, math.pi * 0.5, 0)))
		
		
		self.game_interface.set_game_state(GameState(cars=car_states))
		return StepResult(beat - start_time>0.2, 0)

	def drift_downward(self, packet, drone, start_time) -> StepResult:
		"""
		Causes cars to boost and pitch until they land on their wheels. This is tuned to work well when
		place_near_ceiling has just been called.
		"""
		drone.ctrl = SimpleControllerState(boost=drone.vel[2] < -280, throttle=1, pitch=-0.15)
		wheel_contact = packet.game_cars[drone.index].has_wheel_contact
		return StepResult(finished=wheel_contact)

	def initial_setup(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Places the ball above the roof of the arena to keep it out of the way.
		"""
		self.game_interface.set_game_state(GameState(ball=BallState(physics=Physics(
			location=Vector3(0, 0, 100),
			velocity=Vector3(0, 0, -2000),
			angular_velocity=Vector3(0, 0, 0))), cars={
				0:CarState(physics=Physics(velocity=Vector3(0, 0, 0), location=Vector3(0, -600, 15), rotation=Rotator(0, math.pi * 0.5, 0)))}))
		return StepResult(finished=True)

	def zero_velocity(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Places the ball above the roof of the arena to keep it out of the way.
		"""
		self.game_interface.set_game_state(GameState(cars={
				0:CarState(physics=Physics(location=Vector3(0, 200, 500), velocity=Vector3(0, 0, 0)))}))
		return StepResult(finished=True)


	def hide_ball(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Places the ball above the roof of the arena to keep it out of the way.
		"""
		self.game_interface.set_game_state(GameState(ball=BallState(
			physics=Physics(location=Vector3(9000, 0, 0), velocity=Vector3(0, 0, 0))
		), console_commands=["Set WorldInfo WorldGravityZ -650", "Set WorldInfo TimeDilation 1"]))
		return StepResult(finished=True)
	
	def make_sure_all_cars_spawn(self, packet, drones, start_time, beat):
		self.game_interface.set_game_state(GameState(console_commands=["Set WorldInfo WorldGravityZ 900"]))
		return StepResult(finished=True)

	def setup_ball(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Places the ball above the roof of the arena to keep it out of the way.
		"""
		self.game_interface.set_game_state(GameState(ball=BallState(
			physics=Physics(location=Vector3(0, 0, 1000), velocity=Vector3(0, 0, 0))
		))) #, cars={
			#	0:CarState(physics=Physics(location=Vector3(0, 0, 900), velocity=Vector3(0, 0, 0), rotation=Rotator(math.pi * 0.5, 0, 0)))}))
		return StepResult(finished=True)
	
	def two_car_setup(self, packet, drones, start_time, beat) -> StepResult:
		"""
		Places the ball above the roof of the arena to keep it out of the way.
		"""
		self.game_interface.set_game_state(GameState(cars={
				0:CarState(physics=Physics(location=Vector3(0, -4000, 0), velocity=Vector3(0, 0, 0), rotation=Rotator(0, math.pi * 1.25, 0))),
				1:CarState(physics=Physics(location=Vector3(0, 4000, 0), velocity=Vector3(0, 0, 0), rotation=Rotator(0, math.pi * 1.25, 0)))}))
		return StepResult(finished=True)

