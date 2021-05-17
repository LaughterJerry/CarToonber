#!/usr/bin/env python3

import pygame
from pygame.locals import Color
from listener import Key_listener

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

import os
import random
import copy

from OBJ2D import OBJ2D
import verts
import track


class PygameWindow:
	def __init__(self, width, height, title, listener):
		pygame.init()


		self.title = title
		self.width = width
		self.height = height

		self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF|OPENGL)

		self.face_f = OBJ2D("rig/head_f.png", self, 1)
		self.face_r = OBJ2D("rig/head_r.png", self, 1)
		self.face_l = OBJ2D("rig/head_l.png", self, 1)

		self.eye_f = OBJ2D("rig/eye_f.png", self, .6)
		self.eye_r = OBJ2D("rig/eye_r.png", self, .6)
		self.eye_l = OBJ2D("rig/eye_l.png", self, .6)

		self.eye_c = OBJ2D("rig/eye_c.png", self, .6)

		self.eyebrow = OBJ2D("rig/eyebrow.png", self, .5)

		self.mouth_c = OBJ2D("rig/mouth_closed.png", self, .3, zero=True)
		self.mouth_o = OBJ2D("rig/mouth_open.png", self, .3, zero = True)

		self.front_hair = OBJ2D("rig/front_hair.png", self, 1.1)

		self.tress_1 = OBJ2D("rig/tress_1.png", self, 1, zero=True, grav=True)
		self.tress_2 = OBJ2D("rig/tress_2.png", self, 1, zero=True, grav=True)

		self.ear_r = OBJ2D("rig/ear.png", self, .6, zero=True)
		self.ear_l = OBJ2D("rig/ear.png", self, .6, zero=True)

		self.ear_l.set_scale_x(-1)

		self.hat = OBJ2D("rig/hat.png", self, 2)

		self.body = OBJ2D("rig/body.png", self, 2, zero=True)

		self.screen_rect = self.screen.get_rect()
		self.listener = listener

		pygame.display.set_caption(self.title)
		self.tracker = track.facial_track()


		self.clock = pygame.time.Clock()

		glClearColor(0,0,1,1)
		self.Purge()

		self.test = 0.0
		self.change = .05

	def Purge(self):
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		glViewport(0,0, self.width, self.height)
		glLoadIdentity()
		gluPerspective(45, (self.width/ self.height), 0.1, 50.0)
		glTranslatef(0.0,0.0,-5)
		glRotatef(0,0,0,0)

	def update(self):

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				self.listener.set_keydown(event.key)
			if event.type == pygame.KEYUP:
				self.listener.set_keyup(event.key)		

		self.tracker.update()
		self.tracker.draw()
		#self.tracker.output()

		self.test = self.tracker.get_nose_pos()
		self.test[0] -= .5
		self.test[1] -= .7

		roll = self.tracker.get_roll()
		eyer = self.tracker.get_right_eye()
		eyel = self.tracker.get_left_eye()
		eye_lim = .10

		mouth = self.tracker.get_mouth()
		mouth_lim = .10

		smile = self.tracker.get_smile()

		ear_offset_pos = self.test[0]*.5+1.3
		ear_offset_neg = 1.3-self.test[0]*.5

		#self.tress_1.move_center(self.test)
		self.hat.move([-self.test[0]*.1,(-self.test[1])+.2])
		self.hat.rotate(roll)
		self.hat.draw_image()

		self.body.move([0,-.3])
		self.body.draw_image()

		if self.test[0] < -.15:
			self.ear_l.move([ -ear_offset_pos ,self.test[1]+.5])
			self.ear_l.rotate(roll)
			self.ear_l.draw_image()

			#self.tress_1.move_center(self.test)
			self.tress_1.move([self.test[0]*.5-.8,self.test[1]+.6])
			self.tress_1.rotate(roll)
			self.tress_1.draw_image()

			self.face_l.move_center(self.test)
			self.face_l.rotate(roll )
			self.face_l.draw_image()

			if eyer < eye_lim or eyel < eye_lim :
				self.eye_c.move_center(self.test )
				self.eye_c.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_c.rotate(roll )
				self.eye_c.draw_image()
			else:
				self.eye_l.move_center(self.test )
				self.eye_l.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_l.rotate(roll )
				self.eye_l.draw_image()

			self.eyebrow.move_center(self.test)
			self.eyebrow.move([self.test[0]*.5,self.test[1]+.3])
			self.eyebrow.rotate(roll )
			self.eyebrow.draw_image()

			self.ear_r.move([ ear_offset_pos ,self.test[1]+.5])
			self.ear_r.rotate(roll)
			self.ear_r.draw_image()

			#self.tress_2.move_center(self.test)
			self.tress_2.move([self.test[0]*.5+.8,self.test[1]+.6])
			self.tress_2.rotate(roll)
			self.tress_2.draw_image()

		elif self.test[0] > .15:

			self.ear_r.move([ ear_offset_neg,self.test[1]+.5])
			self.ear_r.rotate(roll)
			self.ear_r.draw_image()

			#self.tress_2.move_center(self.test)
			self.tress_2.move([self.test[0]*.5+.8,self.test[1]+.6])
			self.tress_2.rotate(roll)
			self.tress_2.draw_image()

			self.face_r.move_center(self.test)
			self.face_r.rotate(roll )
			self.face_r.draw_image()

			if eyer < eye_lim or eyel < eye_lim:
				self.eye_c.move_center(self.test )
				self.eye_c.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_c.rotate(roll )
				self.eye_c.draw_image()
			else:
				self.eye_r.move_center(self.test )
				self.eye_r.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_r.rotate(roll )
				self.eye_r.draw_image()

			self.eyebrow.move_center(self.test)
			self.eyebrow.move([self.test[0]*.5,self.test[1]+.3])
			self.eyebrow.rotate(roll )
			self.eyebrow.draw_image()

			self.ear_l.move([ -ear_offset_neg,self.test[1]+.5])
			self.ear_l.rotate(roll)
			self.ear_l.draw_image()

			#self.tress_1.move_center(self.test)
			self.tress_1.move([self.test[0]*.5-.8,self.test[1]+.6])
			self.tress_1.rotate(roll)
			self.tress_1.draw_image()

		else:
			if self.test[0] > 0:
				self.ear_r.move( [ear_offset_neg,self.test[1]+.5])
				self.ear_l.move( [-ear_offset_neg,self.test[1]+.5])
			else:
				self.ear_r.move( [ear_offset_neg,self.test[1]+.5])
				self.ear_l.move( [-ear_offset_neg,self.test[1]+.5])

			self.ear_r.rotate(roll)
			self.ear_r.draw_image()

			self.ear_l.rotate(roll)
			self.ear_l.draw_image()

			self.face_f.move_center(self.test)
			self.face_f.rotate(roll )
			self.face_f.draw_image()

			if eyer < eye_lim or eyel < eye_lim:
				self.eye_c.move_center(self.test )
				self.eye_c.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_c.rotate(roll )
				self.eye_c.draw_image()
			else:
				self.eye_f.move_center(self.test )
				self.eye_f.move([self.test[0]*.5,self.test[1]-.1])
				self.eye_f.rotate(roll)
				self.eye_f.draw_image()

			self.eyebrow.move_center(self.test)
			self.eyebrow.move([self.test[0]*.5,self.test[1]+.3])
			self.eyebrow.rotate(roll )
			self.eyebrow.draw_image()

			#self.tress_1.move_center(self.test)
			self.tress_1.move([self.test[0]*.5-.8,self.test[1]+.6])
			self.tress_1.rotate(roll)
			self.tress_1.draw_image()

			#self.tress_2.move_center(self.test)
			self.tress_2.move([self.test[0]*.5+.8,self.test[1]+.6])
			self.tress_2.rotate(roll)
			self.tress_2.draw_image()

		if mouth > mouth_lim:
			self.mouth_o.move_center(self.test)
			self.mouth_o.set_scale_y(mouth*3)
			self.mouth_o.set_scale_x((smile+1))
			self.mouth_o.move([self.test[0]*.5,self.test[1]-.6])
			self.mouth_o.rotate(roll )
			self.mouth_o.draw_image()
		else:
			self.mouth_c.move_center(self.test)
			self.mouth_c.set_scale_x((smile+1))
			self.mouth_c.move([self.test[0]*.5,self.test[1]-.6])
			self.mouth_c.rotate(roll )
			self.mouth_c.draw_image()

		self.front_hair.move_center(self.test)
		self.front_hair.move([self.test[0]*.5,self.test[1]+.6])
		self.front_hair.rotate(roll)
		self.front_hair.draw_image()

		pygame.display.flip()
		self.Purge()

		self.clock.tick()
		print(self.clock.get_fps())


if __name__ == '__main__':
	win = PygameWindow(800,600,"VTuber Display Window", Key_listener())

	while not win.listener.get_key(pygame.K_q):	
		win.update()
