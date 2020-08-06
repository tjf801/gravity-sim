import pyglet, math
#from random import randint

dt = 1/120
G = 2e4

class Force:
	def __init__(self, x: float, y: float):
		self.x = x
		self.y = y
	def __repr__(self):
		return f"Force(x={self.x}, y={self.y})"
	def __add__(self, other):
		return Force(self.x+other.x, self.y+other.y)
	def __neg__(self):
		return Force(-self.x, -self.y)

class Planet:
	def __init__(self, mass: float, x: float, y: float, x_velocity:float=0, y_velocity:float=0, color:tuple=(255,255,255)):
		self.x = x
		self.y = y
		self.x_velocity = x_velocity
		self.y_velocity = y_velocity
		self.mass = mass
		self.radius = math.ceil(math.sqrt(abs(self.mass))) if abs(self.mass)>10 else 4
		self.color = color
	
	def get_net_force(self, planets:list) -> Force:
		net_force = Force(0., 0.)
		for planet in planets:
			if planet is self: continue
			dx = self.x-planet.x
			dy = self.y-planet.y
			distance_squared = dx*dx + dy*dy #square pixels
			distance = math.sqrt(distance_squared) #pixels
			magnitude = (G*self.mass*planet.mass)/distance_squared if distance_squared>1e-5 else 0. #Force (kg pixel/sec^2)
			force = -Force(magnitude*(dx/distance), magnitude*(dy/distance))
			net_force += force
		return net_force
	
	def update_velocity(self, planets:list):
		net_force = self.get_net_force(planets)
		self.x_velocity += (net_force.x/self.mass)*dt
		self.y_velocity += (net_force.y/self.mass)*dt
	
	def update_position(self):
		self.x += self.x_velocity*dt
		self.y += self.y_velocity*dt
	
	def __repr__(self):
		return f"Planet(mass={self.mass}, x={self.x}, y={self.y}, x_velocity={self.x_velocity}, y_velocity={self.y_velocity})"
	
	def draw(self):
		pyglet.shapes.Circle(x=self.x, y=self.y, radius=self.radius, color=self.color).draw()

window = pyglet.window.Window(600, 600, resizable=True, vsync=True)
planets = [Planet(100, 300., 300., 0., -25., color=(0,0,255)), Planet(25., 400., 300., 0., 100.)] #planets = [Planet(randint(0,100), randint(0,600), randint(0,600), randint(-50,100), randint(-50,100), color=(randint(0,255),randint(0,255),randint(0,255))) for _ in range(3)]

def update(_):
	window.clear()
	
	for p in planets: p.update_velocity(planets)
	for p in planets: p.update_position(); p.draw()
	
	print(f"x momentum:{round(sum(p.mass*p.x_velocity for p in planets),3)} y momentum:{round(sum(p.mass*p.y_velocity for p in planets),3)}", end='\r')
	
	#collisions
	for p1 in planets:
		for p2 in planets:
			if p1 is p2: continue
			sq_distance = (p1.x-p2.x)*(p1.x-p2.x)+(p1.y-p2.y)*(p1.y-p2.y)
			sq_sum_radii = (p1.radius+p2.radius)*(p1.radius+p2.radius)
			#collision check
			if sq_distance <= sq_sum_radii:
				# create combined planet
				new_x = (p1.mass*p1.x + p2.mass*p2.x)/(p1.mass+p2.mass)
				new_y = (p1.mass*p1.y + p2.mass*p2.y)/(p1.mass+p2.mass)
				new_x_velocity = (p1.mass*p1.x_velocity + p2.mass*p2.x_velocity)/(p1.mass+p2.mass)
				new_y_velocity = (p1.mass*p1.y_velocity + p2.mass*p2.y_velocity)/(p1.mass+p2.mass)
				# weighted "average" of the two colors idk
				new_color = tuple(int((a*p1.mass+b*p2.mass)/(p1.mass+p2.mass)) for a, b in zip(p1.color, p2.color))
				planets.append(Planet(p1.mass+p2.mass, new_x, new_y, new_x_velocity, new_y_velocity, color=new_color))
				# remove old planets
				planets.remove(p1)
				planets.remove(p2)

pyglet.clock.schedule_interval(update, dt)
pyglet.app.run()