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

import verts


class OBJ2D:
	def __init__(self, pathname, canvas, scale, zero=False, grav=False):
		self.pathname = pathname
		self.canvas = canvas
		self.scale = scale
		self.grav = grav
		if zero:
			self.verts = copy.deepcopy(verts.verts_0)
			self.t_verts = copy.deepcopy(verts.verts_0)
			self.coords = copy.deepcopy(verts.coords_0)
		else:
			self.verts = copy.deepcopy(verts.verts)
			self.t_verts = copy.deepcopy(verts.verts)
			self.coords = copy.deepcopy(verts.coords)

		self.edges = copy.deepcopy(verts.edges)
		self.loaded = False
		self.x_pos = 0.0
		self.y_pos = 0.0

		self.texture = None

		self.roll = 0
		self.turn = 0.0

		self.x_origin = 0
		self.y_origin = 0

		self.scale_x = 1
		self.scale_y = 1

		self.load_texture()

	def set_scale_x(self, x):
		self.scale_x = x

	def set_scale_y(self, y):
		self.scale_y = y

	def move(self, pos):
		self.x_origin = pos[0]
		self.y_origin = pos[1]

	def move_pos(self, pos):
		x_pos, y_pos = pos

		self.x_pos = x_pos
		self.y_pos = y_pos


	def move_center(self, pos):
		self.move_pos(pos)

		for x in range(len(self.verts)):
			if self.verts[x][0] == 0:
				pass
			elif self.verts[x][0] < 0:
				self.t_verts[x][0] = self.verts[x][0] - (self.x_pos)
			elif self.verts[x][0] > 0:
				self.t_verts[x][0] = self.verts[x][0] - (self.x_pos)


		for y in range(len(self.verts)):
			if self.verts[y][1] == 0:
				pass
			elif self.verts[y][1] < 0:
				self.t_verts[y][1] = self.verts[y][1] - (self.y_pos)
			elif self.verts[y][1] > 0:
				self.t_verts[y][1] = self.verts[y][1] - (self.y_pos)

	def rotate(self, angle):
		self.roll = angle

	def transform(self):
		glTranslatef(self.x_pos, self.y_pos, 0)
		glRotatef(self.roll, 0, 0, 1)
		glTranslatef(self.x_origin, self.y_origin, 0)
		if self.grav:
			glRotatef(-self.roll, 0, 0, 1)

		glScalef(self.scale*self.scale_x,self.scale*self.scale_y,1.0)

	def prepTexture(self):
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glEnable(GL_BLEND)

	def drawTexture(self):
		glBegin(GL_POLYGON)

		for x in range(len(self.t_verts)):
			glTexCoord2f(*self.coords[x])
			glVertex3f(*self.t_verts[x])

		glEnd()
		glDisable(GL_BLEND)

	def begin(self):
		glPushMatrix()

	def end(self):
		glPopMatrix()

	def draw_image(self):
		self.begin()
		self.transform()
		self.prepTexture()
		self.drawTexture()
		self.end()

	def load_texture(self):
		textureSurface = pygame.image.load(self.pathname)
		textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

		self.width = textureSurface.get_width()
		self.height = textureSurface.get_height()

		if self.width > self.height:
			ratio = self.height/self.width
			for x in range(len(self.verts)):
				self.verts[x][1] *= ratio

		else:
			ratio = self.width/self.height
			for x in range(len(self.verts)):
				self.verts[x][0] *= ratio

		self.t_verts = copy.deepcopy(self.verts)

		self.loaded = True

		glEnable(GL_TEXTURE_2D)
		self.texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texture)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height,
					0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
		glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

		glGenerateMipmap(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, 0)
