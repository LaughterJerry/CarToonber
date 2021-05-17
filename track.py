import cv2
import dlib
import numpy as np
import math
from scipy.spatial import distance as dist

class facial_track:
	def __init__(self):
		self.detector = dlib.get_frontal_face_detector()
		self.predictor = dlib.shape_predictor('shape_68.dat')

		self.cap = cv2.VideoCapture(0)
		self.ret, self.img = self.cap.read()

		self.kernel = np.ones((9,9), np.uint8)

		self.shape = []
		self.static_shape = []

		self.yaw = 0
		self.roll = 0
		self.pitch = 0
		self.origin = [0,0]

		self.right_eye = 0
		self.left_eye = 0
		self.mouth = 0
		self.smile = 0

		self.origin_avg = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],]
		self.roll_avg = 	[0,0,0,]
		self.pitch_avg = 	[0,0,0,]
		self.yaw_avg = 		[0,0,0,]

		self.nose_pos_x = [0,0,0]
		self.nose_pos_y = [0,0,0]

	def average(self, lst): 
		return sum(lst) / len(lst) 

	def feature_aspect_ratio(self, feature):
		#takes six points and compares the aspect ratio to determine if open
		"""
			1	2
		0			3
			5	4
		"""

		A = dist.euclidean(feature[1], feature[5])
		B = dist.euclidean(feature[2], feature[4])
		C = dist.euclidean(feature[0], feature[3])

		FAR = (A + B) / (2.0 * C)

		return FAR

	def shape_to_np(self, shape, dtype="int"):
		# initialize the list of (x, y)-coordinates
		coords = np.zeros((68, 2), dtype=dtype)
		# loop over the 68 facial landmarks and convert them
		# to a 2-tuple of (x, y)-coordinates
		for i in range(0, 68):
			coords[i] = (shape.part(i).x, shape.part(i).y)
		# return the list of (x, y)-coordinates
		return coords

	def rotate_point(self, pos, img, angle):
		if angle == 0: return pos
		x = pos[0] - img.shape[1]*0.4
		y = pos[1] - img.shape[0]*0.4
		newx = x*math.cos(math.radians(angle)) + y*math.sin(math.radians(angle)) + img.shape[1]*0.4
		newy = -x*math.sin(math.radians(angle)) + y*math.cos(math.radians(angle)) + img.shape[0]*0.4
		return int(newx), int(newy)

	def gen_yaw(self):
		yaw1 = (self.shape[30][0] - self.shape[16][0])
		yaw2 = (self.shape[0][0] - self.shape[30][0])
		#swap - if head isn't turning the right way
		if yaw1 > yaw2:
			yaw = 40*(1-(yaw1/yaw2))
		else:
			yaw = 40*(-(1-(yaw2/yaw1)))

		f_width = self.shape[16][0] - self.shape[0][0]
		nose_pos = (self.shape[30][0]-self.shape[0][0])/f_width
		self.nose_pos_x.pop(0)
		self.nose_pos_x.append(nose_pos)

		self.yaw_avg.pop(0)
		self.yaw_avg.append(yaw)
		self.yaw = self.average(self.yaw_avg)

	def gen_pitch(self):
		pitch1 = self.shape[8][1] - self.shape[30][1]
		pitch2 = self.shape[30][1] - self.shape[27][1]
		pitch = -((pitch1/pitch2 - 2.15) * 26)

		f_height = self.shape[27][1] - self.shape[8][1]
		nose_pos = (self.shape[30][1] - self.shape[8][1])/f_height

		self.nose_pos_y.pop(0)
		self.nose_pos_y.append(nose_pos)

		self.pitch_avg.pop(0)
		self.pitch_avg.append(pitch)
		self.pitch = self.average(self.pitch_avg)

	def gen_roll(self):
		x1, y1 = self.shape[27]
		x2, y2 = self.shape[8]

		if x1 < x2:
			roll = 90-math.degrees(math.atan((y2-y1)/(x2-x1)))
		elif x1 > x2:
			roll = -(90+math.degrees(math.atan((y1-y2)/(x1-x2))))
		else:
			roll = 0

		self.roll_avg.pop(0)
		self.roll_avg.append(roll)
		self.roll = self.average(self.roll_avg)

	def gen_static(self):

		self.static_shape = []

		side = self.rotate_point(self.shape[0], self.img, -self.roll)
		top = self.rotate_point(self.shape[27], self.img, -self.roll)

		for pos in self.shape:
			n_point = self.rotate_point(pos, self.img, -self.roll)
			n_point = [n_point[0]-side[0], n_point[1]-top[1]+50]
			self.static_shape.append(n_point)

	def gen_origin(self):
		cur_origin =[ self.shape[0][0]+int((self.shape[16][0]-self.shape[0][0])/2), self.shape[27][1]+int((self.shape[8][1] - self.shape[27][1])/2)]		
		width = self.img.shape[0]/2
		height = self.img.shape[1]/2
		#a temporary measure, when making final product swap out 1.275 and -.256 for learned center
		temp_origin = [(4*(cur_origin[0]-width)/width)-1.275, -((2*(cur_origin[1]-height)/height)+.256) ]
		self.origin_avg.pop(0)
		self.origin_avg.append(temp_origin)
		totx = 0
		toty = 0
		for x in range(len(self.origin_avg) ):
			totx += self.origin_avg[x][0]
			toty += self.origin_avg[x][1]

		self.origin = [totx/ len(self.origin_avg), toty/ len(self.origin_avg) ]

	def update(self):
		self.ret, self.img = self.cap.read()
		gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
		rects = self.detector(gray, 1)
		if len(rects) > 0:
			rect = rects[0]
			self.shape = self.predictor(gray, rect)
			self.shape = self.shape_to_np(self.shape)

		self.gen_yaw()
		self.gen_pitch()
		self.gen_roll()
		self.gen_static()
		self.gen_origin()

		self.right_eye = self.feature_aspect_ratio(self.static_shape[36:42])
		self.left_eye = self.feature_aspect_ratio(self.static_shape[42:48])

		t_mouth = [self.static_shape[49], 
					self.static_shape[61], 
					self.static_shape[63], 
					self.static_shape[55], 
					self.static_shape[65],
					self.static_shape[67]]

		self.mouth = self.feature_aspect_ratio(t_mouth)

		self.smile = ((self.static_shape[54][0]-self.static_shape[48][0])/self.static_shape[16][0])			

	def get_nose_pos(self):
		return [self.average(self.nose_pos_x), self.average(self.nose_pos_y)]

	def get_yaw(self):
		return self.yaw

	def get_pitch(self):
		return self.pitch

	def get_roll(self):
		return self.roll

	def get_origin(self):
		return self.origin

	def get_right_eye(self):
		return self.right_eye

	def get_left_eye(self):
		return self.left_eye

	def get_mouth(self):
		return self.mouth

	def get_smile(self):
		return self.smile

	def draw(self):
		for (x, y) in self.shape:
			cv2.circle(self.img, (x, y), 2, (255, 0, 0), -1)
		for point in [30]:
			cv2.circle(self.img, (self.shape[point][0] , self.shape[point][1]), 2, (0, 0, 255), -1)
		cv2.imshow('face', self.img)

	def output(self):
		print("pitch: %f\nroll: %f\nyaw: %f\norigin: %s\nright eye: %f\nleft eye: %f\nmouth: %f\nsmile: %f\n" % (self.get_pitch(), self.get_roll(), self.get_yaw(), str(self.get_origin()), self.get_right_eye(), self.get_left_eye(), self.get_mouth(), self.get_smile()))


	def destroy(self):
		self.cap.release()
		cv2.destroyAllWindows()

if __name__ == "__main__":
	track = facial_track()
	running = True
	while running:
		track.update()
		track.draw()
		track.output()

		if cv2.waitKey(1) & 0xFF == ord('q'):
			track.destroy()
			running = False