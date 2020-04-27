# Algo devised by: https://github.com/guofei9987/scikit-opt
# Modified to fit this project

import numpy as np
from transformer import fn_transformer

'''
If you are running runPSO.py, change the previous line with:
# from transformer import fn_transformer
'''


class PSO():
	def __init__(self, func, dim, pop=40, max_iter=150, lb=None, ub=None, w=0.8, c1=0.5, c2=0.5):
		self.func = fn_transformer(func)
		self.w = w  # inertia
		self.cp, self.cg = c1, c2  # parameters to control personal best, global best respectively
		self.pop = pop  # number of particles
		self.dim = dim  # dimension of particles, which is the number of variables of func
		self.max_iter = max_iter  # max iter

		self.has_constraints = not (lb is None and ub is None)
		self.lb = -np.ones(self.dim) if lb is None else np.array(lb)
		self.ub = np.ones(self.dim) if ub is None else np.array(ub)
		assert self.dim == len(self.lb) == len(self.ub), 'dim == len(lb) == len(ub) is not True'
		assert np.all(self.ub > self.lb), 'upper-bound must be greater than lower-bound'

		self.X = np.random.uniform(low=self.lb, high=self.ub, size=(self.pop, self.dim))
		v_high = self.ub - self.lb
		self.V = np.random.uniform(low=-v_high, high=v_high, size=(self.pop, self.dim))  # speed of particles
		self.Y = self.cal_y()  # y = f(x) for all particles
		self.pbest_x = self.X.copy()  # personal best location of every particle in history
		self.pbest_y = self.Y.copy()  # best image of every particle in history
		self.gbest_x = np.zeros((1, self.dim))  # global best location for all particles
		self.gbest_y = 0  # global best y for all particles
		self.gbest_y_hist = []  # gbest_y of every iteration
		self.update_gbest()

		# record verbose values
		self.record_mode = False
		self.record_value = {'X': [], 'V': [], 'Y': []}

	def update_V(self):
		r1 = np.random.rand(self.pop, self.dim)
		r2 = np.random.rand(self.pop, self.dim)
		self.V = self.w * self.V + \
		self.cp * r1 * (self.pbest_x - self.X) + \
		self.cg * r2 * (self.gbest_x - self.X)

	def update_X(self):
		self.X = self.X + self.V

		if self.has_constraints:
			self.X = np.clip(self.X, self.lb, self.ub)

	def cal_y(self):
		# calculate y for every x in X
		self.Y = self.func(self.X).reshape(-1, 1)
		return self.Y

	def update_pbest(self):
		self.pbest_x = np.where(self.pbest_y < self.Y, self.X, self.pbest_x)
		self.pbest_y = np.where(self.pbest_y < self.Y, self.Y, self.pbest_y)

	def update_gbest(self):
		if self.gbest_y < self.Y.max():
			self.gbest_x = self.X[self.Y.argmin(), :].copy()
			self.gbest_y = self.Y.min()

	def recorder(self):
		if not self.record_mode:
			return
		self.record_value['X'].append(self.X)
		self.record_value['V'].append(self.V)
		self.record_value['Y'].append(self.Y)

	def run(self, max_iter=None):
		print("Running PSO...")
		self.max_iter = max_iter or self.max_iter
		for iter_num in range(self.max_iter):
			print("\tIteration ",iter_num," complete")
			self.update_V()
			self.recorder()
			self.update_X()
			self.cal_y()
			self.update_pbest()
			self.update_gbest()

		self.gbest_y_hist.append(self.gbest_y)
		return self

	fit = run
