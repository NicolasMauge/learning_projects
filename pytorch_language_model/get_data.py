"""
This program will take three files (train / valid / test) and 
return three iterators :
						n_batch-->
		articles
			|			
			|
			V
"""
import random
import numpy as np
from utils.utils import get_num_lines, hms_string, save_vocabulary, load_vocabulary
import time

import torch

bptt = 70

def load_data(filename):
	with open(filename, "r") as file:
		for line in file:
			yield line

def load_data_np(filename):
	with open(filename, "r") as file:
		for line in file:
			yield np.array(line.rstrip().split(";"))

class get_data():
	def __init__(self, bptt, filenames, n_batch=64, phase="train"):
		self.bptt = bptt
		self.phases = ["train", "valid", "test"]
		self.n_batch = n_batch
		self.set_phase(phase)
		self.data = None

		if isinstance(filenames, dict):
			if [data_set in filenames for data_set in self.phases] == [True]*3:
				self.filenames = filenames
			else:
				raise ValueError(f"The parameter 'filenames'={filenames} don't have the 'train', 'valid' and 'test' keys")
		else:
			raise ValueError(f"The parameter 'filenames'={filenames} is not a dictionnary")
		

	def set_phase(self, phase):
		if phase in self.phases:
			self.phase=phase
		else:
			raise ValueError(f"Phase parameter (={phase}) must be 'train', 'test' or 'valid'")

	@staticmethod
	def split(filename, proportions=[0.7, 0.15, 0.15]):
		"""
		This function splits the main file in 3 files (train / valid / test)
		"""
		with open(filename[:-4]+"_train.csv", "w") as file_train:
			with open(filename[:-4]+"_valid.csv", "w") as file_valid:
				with open(filename[:-4]+"_test.csv", "w") as file_test:
					for article in load_data(filename):
						p = np.random.uniform()
						if p<proportions[0]:
							file_train.write(article)
						elif p<proportions[0]+proportions[1]:
							file_valid.write(article)
						else:
							file_test.write(article)

	def len_seq(self):
		# https://github.com/salesforce/awd-lstm-lm/blob/master/main.py
		rand_bptt = self.bptt if np.random.random() < 0.95 else self.bptt / 2.
		return max(5, int(np.random.normal(rand_bptt, 5)))

	def set_batch(self):
		data=[]
		for line in load_data_np(self.filenames[self.phase]):
			data.append(line)

		permutation = np.random.permutation(len(data))
		data = [data[i] for i in permutation]

		data = np.concatenate(data, axis=None)

		len_batch = data.shape[0] // self.n_batch
		data = data[:len_batch*self.n_batch]
		
		data = data.reshape(self.n_batch, -1).astype(int).T

		self.data = torch.from_numpy(data).contiguous()


	def __iter__(self):
		if self.data is None:
			self.set_batch()

		self.index = 0
		while True:
			self.seq_len = self.len_seq()

			if self.index+self.seq_len+1 <= self.data.shape[0]:
				yield self.data[self.index:self.index+self.seq_len], self.data[self.index+1:self.index+self.seq_len+1].view(-1)
				self.index += self.seq_len
			else:
				break


	


if __name__ == '__main__':
	# test 
	filenames = {"train":"data/wiki_text_train.csv", "test":"data/wiki_text_test.csv", "valid":"data/wiki_text_valid.csv"}
	#get_data.split("data/wiki_text.csv")

	data_class = get_data(10, filenames, n_batch=20, phase="train")
	data_class.set_batch()

	print(data_class.data.shape)
		
	#print(next(iter(data_class)))
	



