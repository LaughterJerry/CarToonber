class Key_listener:
	#holds current key states
	def __init__(self):
		self.keymap = []#{v: k for v, k in enumerate([False] * 512 )}
		self.struck = []#[False]*512
		self.mouse_button = []#[False]*30
		self.mouse_pos = (0,0)

	def set_keydown(self, key):
		self.struck.append(key)
		self.keymap.append(key)

	def set_keyup(self, key):
		if key in self.struck:
			self.struck.remove(key)
		if key in self.keymap:
			self.keymap.remove(key)


	def set_mouse_down(self, button):
		"""
		event.button: [1:left, 2:middle, 3:right, 4:scroll up, 5:scroll down]
		"""
		self.mouse_button.append(button)

	def set_mouse_up(self, button):
		self.mouse_button.remove(button)

	def set_mouse_pos(self, pos):
		xpos = (pos[0]*.0129) - 7.35
		ypos = ((pos[1]*.0129) - 4.12) * -1
		self.mouse_pos = (xpos,ypos)

	def get_mouse_button(self, button):
		print(self.mouse_button)
		return self.mouse_button[button]

	def get_mouse_pos(self):
		return self.mouse_pos

	def get_key(self, key):
		return (key in self.keymap)

	def get_state(self):
		return copy.deepcopy(self.keymap)

	def get_struck(self, key):
		return (key in self.struck)

	def clear_struck(self):
		self.struck = []

	def get_all(self):
		return [k for k,v in self.keymap.items() if v == True]
