import pygame
#
class Button:
	def __init__(self, rect, colour, text="", font=None, antialiasing=True, text_colour=(0, 0, 0)):
		self.x, self.y, self.w, self.h = rect
		self.colour = colour
		self.text_render = None
		self.pressed = False
		self.text = text
		self.antialiasing = antialiasing
		self.text_colour = text_colour
		self.font = font
		self.coords = []
		for x in range(self.x, self.x + self.w + 1): # x, x + width + 1
			for y in range(self.y, self.y + self.h + 1):
				self.coords.append((x, y))
		self.button = pygame.sprite.Sprite()
		self.button.rect = pygame.Rect(self.x, self.y, self.w, self.h)
		self.button.image = pygame.Surface((self.w, self.h))
		self.button.image.fill(self.colour)
		if self.text:
			self.text_render = font.render(self.text, self.antialiasing, self.text_colour)

	def press(self):
		if self.pressed:
			self.pressed = False
		else:
			self.pressed = True

	def get_button(self):
		return self.button

	def check_press(self, mouse_coords):
		mx, my = mouse_coords
		if (mx, my) in self.coords:
			return True
		return False

	def set_colour(self, colour):
		self.colour = colour

	def set_text(self, text, font, colour, antialiasing=True):
		self.text = text
		self.text_colour
		self.text_render = font.render(self.text, self.antialiasing, self.text_colour)
