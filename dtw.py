'''
/*******************************************************************************
 * Copyright (C) 2018 Francois Petitjean
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 ******************************************************************************/
'''
from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce
import copy


def performDBA(series, penalty=0.5, n_iter=2):
	''' High-level DBA algorithm. '''

	# initialize DP matrices
	length = series.shape[1]
	cost_mat = np.zeros((length, length))
	delta_mat = np.zeros((length, length))
	path_mat = np.zeros((length, length), dtype=np.int8)

	# initialize center
	medoid_ind = approximate_medoid_index(series, cost_mat, delta_mat, penalty)
	center = series[medoid_ind]

	# iteratively update estimate of center
	for i in range(0,n_iter):
		center = DBA_update(center, series, cost_mat, path_mat, delta_mat, penalty)

	# align signals to center
	aligned = DBA_align(center, series, cost_mat, path_mat, delta_mat, penalty)

	return (aligned, center)



def approximate_medoid_index(series, cost_mat, delta_mat, penalty=0.5):
	''' Calculate approximate medoid for DBA initialization. '''

	if series.shape[0] <= 5: # use all data
		indices = range(0, series.shape[0])
	else: # select 5 random indices
		indices = np.random.choice(range(0,series.shape[0]),5,replace=False)

	# return index which minimizes sum-squared DTW error
	medoid_ind = -1
	best_ss = 1e20
	for index_candidate in indices:
		candidate = series[index_candidate]
		ss = sum(map(lambda t:squared_DTW(candidate,t,cost_mat,delta_mat,penalty),series))
		if(medoid_ind==-1 or ss<best_ss):
			best_ss = ss
			medoid_ind = index_candidate
	return medoid_ind



def DTW(s,t,cost_mat,delta_mat,penalty=0.5):
	''' Calculate DTW using intermediate results. '''

	return np.sqrt(squared_DTW(s,t,cost_mat,delta_mat, penalty))



def squared_DTW(s, t, cost_mat, delta_mat, penalty=0.5):
	''' Calculate DTW^2 using DP alignment matrix. '''

	# initialize delta_mat with pairwise distances ED^2
	np.subtract.outer(s, t, out=delta_mat)
	np.square(delta_mat, out=delta_mat)
	scale = np.mean(delta_mat)
	
	# initialize borders of cost matrix
	length = len(s)
	cost_mat[0, 0] = delta_mat[0, 0]
	for i in range(1, length):
		cost_mat[i, 0] = cost_mat[i-1, 0]+delta_mat[i, 0] + scale*penalty
		cost_mat[0, i] = cost_mat[0, i-1]+delta_mat[0, i] + scale*penalty

	# compute cost matrix
	# TODO: return alignment as well
	for i in range(1, length):
		for j in range(1, length):
			diag = cost_mat[i-1, j-1]
			left = cost_mat[i, j-1] + scale*penalty
			top = cost_mat[i-1, j] + scale*penalty
			if(diag <= left):
				if(diag <= top):
					res = diag
				else:
					res = top
			else:
				if(left <= top):
					res = left
				else:
					res = top
			cost_mat[i, j] = res+delta_mat[i, j]
	
	# return alignment score
	return cost_mat[length-1, length-1]



def DBA_update(center, series, cost_mat, path_mat, delta_mat, penalty=0.1):
	''' Update DBA estimate of center. '''

	# define backtracking constants
	DONE = -1
	DIAG = 0
	LEFT = 1
	TOP  = 2

	# all valid backtracking moves
	moves = [(-1, -1), (0, -1), (-1, 0)]

	# initialize results
	updated_center = np.zeros(center.shape)
	n_elements = np.array(np.zeros(center.shape), dtype=int)

	# backtrack each time series
	length = len(center)
	for s in series:

		# initialize delta_mat with pairwise distances
		np.subtract.outer(center, s, out=delta_mat)
		np.square(delta_mat, out=delta_mat)
		scale = np.mean(delta_mat)

		# initialize borders of path and cost matrices
		cost_mat[0, 0] = delta_mat[0, 0]
		path_mat[0, 0] = DONE
		for i in range(1, length):
			cost_mat[i, 0] = cost_mat[i-1, 0]+delta_mat[i, 0] + scale*penalty
			cost_mat[0, i] = cost_mat[0, i-1]+delta_mat[0, i] + scale*penalty
			path_mat[i, 0] = TOP
			path_mat[0, i] = LEFT

		# fill out cost matrix, storing path
		for i in range(1, length):
			for j in range(1, length):
				diag = cost_mat[i-1, j-1]
				left = cost_mat[i, j-1] + scale*penalty
				top = cost_mat[i-1, j] + scale*penalty
				if(diag <=left):
					if(diag<=top):
						res = diag
						path_mat[i,j] = DIAG
					else:
						res = top
						path_mat[i,j] = TOP
				else:
					if(left<=top):
						res = left
						path_mat[i,j] = LEFT
					else:
						res = top
						path_mat[i,j] = TOP
				cost_mat[i, j] = res+delta_mat[i, j]

		# initialize backtrack pointer
		i = length-1
		j = length-1

		# backtrack through path matrix
		while(path_mat[i, j] != -1):

			# store values (and count them) aligned to each center position
			updated_center[i] += s[j]
			n_elements[i] += 1
			
			# update backtrack pointer
			move = moves[path_mat[i, j]]
			i += move[0]
			j += move[1]

		assert(i == 0 and j == 0) # check that we backtracked correctly

		# final update with last data point
		updated_center[i] += s[j]
		n_elements[i] += 1

	# calculate new center as average of values aligned to each position
	return np.divide(updated_center, n_elements)



def DBA_align(center, series, cost_mat, path_mat, delta_mat, penalty=0.1):
	''' Update DBA estimate of center. '''

	aligned = np.zeros_like(series)

	# define backtracking constants
	DONE = -1
	DIAG = 0
	LEFT = 1
	TOP  = 2

	# all valid backtracking moves
	moves = [(-1, -1), (0, -1), (-1, 0)]

	# initialize results
	updated_center = np.zeros(center.shape)
	n_elements = np.array(np.zeros(center.shape), dtype=int)

	# backtrack each time series
	length = len(center)
	for idx, signal in enumerate(series):
		n_elements = np.array(np.zeros(center.shape), dtype=int)

		# initialize delta_mat with pairwise distances
		np.subtract.outer(center, signal, out=delta_mat)
		np.square(delta_mat, out=delta_mat)
		scale = np.mean(delta_mat)

		# initialize borders of path and cost matrices
		cost_mat[0, 0] = delta_mat[0, 0]
		path_mat[0, 0] = DONE
		for i in range(1, length):
			cost_mat[i, 0] = cost_mat[i-1, 0]+delta_mat[i, 0]+scale*penalty
			cost_mat[0, i] = cost_mat[0, i-1]+delta_mat[0, i]+scale*penalty
			path_mat[i, 0] = TOP
			path_mat[0, i] = LEFT

		# fill out cost matrix, storing path
		for i in range(1, length):
			for j in range(1, length):

				# rank possible path options
				diag = cost_mat[i-1, j-1]
				left = cost_mat[i, j-1] + scale*penalty
				top = cost_mat[i-1, j] + scale*penalty
				options = sorted([(diag, DIAG), (left, LEFT), (top, TOP)])
				res, path_mat[i,j] = options[0]

				# update cost matrix with decision
				cost_mat[i, j] = res+delta_mat[i, j]

		# initialize backtrack pointer
		i = length-1
		j = length-1

		# backtrack through path matrix
		while(path_mat[i, j] != DONE):

			# store values (and count them) aligned to each center position
			updated_center[i] += signal[j]
			n_elements[i] += 1

			aligned[idx, i] = signal[j]
			
			# update backtrack pointer
			move = path_mat[i,j]
			move_dir = moves[move]
			i += move_dir[0]
			j += move_dir[1]

		assert(i == 0 and j == 0) # check that we backtracked correctly

		# final update with last data point
		updated_center[i] += signal[j]
		n_elements[i] += 1

	return aligned
