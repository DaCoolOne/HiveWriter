

# Okay, so I have no idea how any of the functions that came with the choreo bot work, so I'm just gonna quietly put my own utils here...


import math

epsilon = 0.000001

def sign(n):
	return -1 if n < 0 else 1

def clamp(n, a, b):
	return min(max(n, a), b)

def clamp_1(n):
	return min(max(n, -1), 1)

def clamp_abs(n, a):
	return min(max(n, -a), a)

def clamp_01(n):
	return min(max(n, 0), 1)

# Used to precent division by zero errors
def not_zero(n):
	return n if abs(n) > epsilon else epsilon * sign(n)

def lerp(a, b, n):
	return (a * (n - 1) + b * n)

# Used by aerial turn controller
def correct(target, val, mult = 1):
	rad = constrain_pi(target - val)
	return (rad * mult)

def constrain_pi(n):
	while n > math.pi:
		n -= math.pi * 2
	while n < -math.pi:
		n += math.pi * 2
	return n


class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, val):
        return Vec3(self.x + val.x, self.y + val.y, self.z + val.z)
    
    def __sub__(self, val):
        return Vec3(self.x - val.x, self.y - val.y, self.z - val.z)
    
    def __mul__(self, val):
        return Vec3(self.x * val, self.y * val, self.z * val)
    
    def sq_length(self):
        return self.x * self.x + self.y * self.y + self.z * self.z
    
    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def set(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def update(self, v):
        self.x = float(v.x)
        self.y = float(v.y)
        self.z = float(v.z)
    
    def align_to(self, rot):
        v = Vec3(self.x, self.y, self.z)
        v.set(v.x, math.cos(rot.roll) * v.y + math.sin(rot.roll) * v.z, math.cos(rot.roll) * v.z - math.sin(rot.roll) * v.y)
        v.set(math.cos(-rot.pitch) * v.x + math.sin(-rot.pitch) * v.z, v.y, math.cos(-rot.pitch) * v.z - math.sin(-rot.pitch) * v.x)
        v.set(math.cos(-rot.yaw) * v.x + math.sin(-rot.yaw) * v.y, math.cos(-rot.yaw) * v.y - math.sin(-rot.yaw) * v.x, v.z)
        return v
    
    def align_from(self, rot):
        v = Vec3(self.x, self.y, self.z)
        v.set(math.cos(rot.yaw) * v.x + math.sin(rot.yaw) * v.y, math.cos(rot.yaw) * v.y - math.sin(rot.yaw) * v.x, v.z)
        v.set(math.cos(rot.pitch) * v.x + math.sin(rot.pitch) * v.z, v.y, math.cos(rot.pitch) * v.z - math.sin(rot.pitch) * v.x)
        v.set(v.x, math.cos(-rot.roll) * v.y + math.sin(-rot.roll) * v.z, math.cos(-rot.roll) * v.z - math.sin(-rot.roll) * v.y)
        return v
    
    def UI_Vec3(self):
        return UI_Vec3(self.x, self.y, self.z)
    
    def copy(self):
        return Vec3(self.x, self.y, self.z)
    
    def flatten(self):
        return Vec3(self.x, self.y, 0)
    
    def normal(self, n = 1):
        l = n / max(self.length(), 0.0001)
        return Vec3(self.x * l, self.y * l, self.z * l)
    
    def tostring(self):
        return str(self.x) + "," + str(self.y) + "," + str(self.z)
    
    def cast(v):
        return Vec3(float(v.x), float(v.y), float(v.z))
    
    def dot(v1, v2):
        return v1.x*v2.x+v1.y*v2.y+v1.z*v2.z
    
    def cross(v1, v2):
        return Vec3(
            v1.y * v2.z - v1.z * v2.y,
            v1.z * v2.x - v1.x * v2.z,
            v1.x * v2.y - v1.y * v2.x
        )
    
    # Returns the angle between two vectors
    def angle_between(v1, v2):
        return math.acos(v1.normal().dot(v2.normal()))
    
    def angle_2d(self):
        return math.atan2(self.y, self.x)
    
    def lerp(v1, v2, t):
        return (v1 * (1-t) + v2 * t)
    def cast_np(v):
        return Vec3(v[0], v[1], v[2])

class Car_Target:
	def __init__(self, pos, up = Vec3()):
		self.pos = pos
		self.up = up

class Rotator:
	
	def __init__(self, yaw = 0, pitch = 0, roll = 0):
		self.yaw = yaw
		self.pitch = pitch
		self.roll = roll
	
	def cast(r):
		return Rotator(r.yaw, r.pitch, r.roll)
	
	def cast_np(r):
		return Rotator(r[1], r[0], r[2])
	
	def angle_between(r1, r2):
		return Vec3(1).align_to(r1).angle_between(Vec3(1).align_to(r2))
	
	def flatten(r):
		return Rotator(r.yaw)
	
	def copy(r):
		return Rotator(r.yaw, r.pitch, r.roll)
	
	def update(self, r):
		self.yaw = float(r.yaw)
		self.pitch = float(r.pitch)
		self.roll = float(r.roll)



def delta_v(packet, phys, position, time, car_vel = None):
	if not car_vel:
		car_vel = Vec3.cast_np(phys.vel)
	car_pos = Vec3.cast_np(phys.pos)
	return Vec3(
		(position.x - car_vel.x * time - car_pos.x) / not_zero(0.5 * time * time),
		(position.y - car_vel.y * time - car_pos.y) / not_zero(0.5 * time * time),
		(position.z - car_vel.z * time - car_pos.z) / not_zero(0.5 * time * time) - packet.game_info.world_gravity_z,
	)

def Align_Car_To(drone, vector, up = Vec3(0, 0, 0)):
	
	car_rot = Rotator.cast_np(drone.rot)
	
	car_rot_vel = Vec3.cast_np(drone.ang_vel)
	
	local_euler = car_rot_vel.align_from(car_rot)
	
	align_local = vector.align_from(car_rot)
	
	local_up = up.align_from(car_rot)
	
	# Improving this
	rot_ang_const = 0.25
	stick_correct = 6.0
	
	a1 = math.atan2(align_local.y, align_local.x)
	a2 = math.atan2(align_local.z, align_local.x)
	
	if local_up.y == 0 and local_up.z == 0:
		a3 = 0.0
	else:
		a3 = math.atan2(local_up.y, local_up.z)
	
	yaw = correct(0.0, -a1 + local_euler.z * rot_ang_const, stick_correct)
	pitch = correct(0.0, -a2 - local_euler.y * rot_ang_const, stick_correct)
	roll = correct(0.0, -a3 - local_euler.x * rot_ang_const, stick_correct)
	
	drone.ctrl.yaw = clamp_1(yaw)
	drone.ctrl.pitch = clamp_1(pitch)
	drone.ctrl.roll = clamp_1(roll)
	
	drone.ctrl.steer = clamp_1(yaw)


def Align_Car_Fast(drone, vector, up, min_dot = 0.8):
	
	car_face = Vec3(1).align_to(Rotator.cast_np(drone.rot))
	
	d = car_face.dot(vector.normal())
	
	if d < min_dot:
		Align_Car_To(drone, vector)
	else:
		Align_Car_To(drone, vector, up)
	
	return d
	


