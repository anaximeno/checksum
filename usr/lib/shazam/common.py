#!/usr/bin/python3
#%load common.py
""" ShaZam  can calculate a file sum and compare with a given one.
ShaZam as also other options like:
	calculate all supported hashsums of one file
	read a file with hash sum and filename inside
	calculate only the file sum without compare it 
Prerequesites:
	python version 3.2.x or higher
	termcolor version 1.1.x or higher (can install it with pip3 or conda)
	alive_progress version 1.6.x or higher (can install it with pip3 or conda)
"""
#### Libraries
# Standart Libraries
import os
import sys
import hashlib as hlib
from time import sleep


def exists(path):
	"""Searchs for a file/path and return bool."""
	return os.path.exists(path)


def print_error(*err, exit=True, err_num=1):
	"""Print the error message and exit.
	Keyword arg: exit -- bool (default True)."""
	error_message = ' '.join(err)
	print("shazam: error: %s" % error_message)	
	if exit: sys.exit(err_num)


try:
	# Third-part libraries
	from termcolor import colored as clr
	from alive_progress import alive_bar
except ImportError:
	print_error("Important Modules are not installed yet: termcolor, " +
	"alive_progress.\nInstall them with: pip (or pip3) install termcolor " +
	"alive_progress")


version = None
if exists("/usr/share/shazam/VERSION"):
	with open("/usr/share/shazam/VERSION", "rt") as ver:
		version = str(ver.read()).strip()

__author__ = "Anaxímeno Brito"
__version__ = version if version else 'Undefined'
__license__ = "GNU General Public License v3.0"
__copyright__ = "Copyright (c) 2020-2021 by " + __author__


# List of all supported hash sums:
sumtypes_list = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
# BUF_SIZE is Constant, don't change it!
BUF_SIZE = 32768
# When lower is the sleep value, faster will be the reading,
# but it will increase the CPU usage, it can be changed to 
# improve the performance.
SLEEP_VALUE = 0.0001 


def hexa_to_int(hexa):
	"""Receive hexadecimal string and return integer."""
	try: return int(hexa, 16)
	except ValueError:
		print_error(f"{hexa!r} is not an hexadecimal value!")


def readable(fname):
	"""Analyses de readability and return bool."""
	if not exists(fname) and not os.path.isfile(fname):
		return False
	try:
		# Try to read, at least, one byte of the file to
		# check if it is readable.
		with open(fname, "rb") as f: 
			f.read(1)
		return True
	except UnicodeDecodeError:
		return False


def get_sumtype(fname):
	"""Analyses the filename and return the sumtype."""
	for stype in sumtypes_list[::-1]:
		if stype in fname: return stype
	return False


def contents(txtfile):
	"""Return a `list with tuples` with the content of the file, 
	each tuple has the following structure: `(filesum, filename)`."""
	if not exists(txtfile):
		print_error(f"{txtfile!r} was not found!")
	elif not readable(txtfile):
		print_error(f"Can't read {txtfile!r}!")
	try:
		with open(txtfile, "rt") as txt:
			content = [(line.split()[0], line.split()[1]) for line in txt]
		if content:	
			return content
		print_error(f"Reading Error: {txtfile!r} is empty!")
	except IndexError:
		print_error(f"Error while reading {txtfile!r}!")
	except UnicodeDecodeError:
		print_error(f"Can't read {txtfile!r}!")


def salutations(string, time_sleep=0.1):
	lines = string.splitlines()
	for line in lines:
		lag = '\r'
		for char in line:
			lag += char
			sys.stdout.write(lag)
			sys.stdout.flush()
			sleep(time_sleep)
		print('')


class FileId(object):
	"""This class holds all necessary informations and operations 
	for one file object."""
	def __init__(self, name, givensum=None):
		# Eliminates asteriscs if there exists one in 
		# the beginning of the file name
		if name[0] == '*' and not exists(name): name = name[1:] 

		self.name = name
		self.existence = exists(name)
		self.readability = readable(name)

		# ´givensum´ is the original file sum which is given
		# at the download place.
		self.gsum = givensum

		# ´self.integer_sum´ is the integer value 
		# of the hash sum, it will be used in comparisons
		# for checking if the values are equal.
		self.integer_sum = hexa_to_int(givensum) if givensum else None

		if readable(name):
			self.size = os.path.getsize(name)
			self.hlist = {
				"md5": hlib.md5(),
				"sha1": hlib.sha1(),
				"sha224": hlib.sha224(),
				"sha256": hlib.sha256(),
				"sha384": hlib.sha384(),
				"sha512": hlib.sha512()
			}

	def get_hashsum(self, sumtype):
		"""Return the file's hash sum."""
		if self.readability:
			return self.hlist[sumtype].hexdigest()
		print_error(f"{self.name!r} is unreadable!")

	def gen_data(self, *, bars=True):
		"""Generates binary data. Keyword arg: bars -- bool (default: True)."""
		if not self.readability:
			print_error(f"{self.name!r} is unreadable!")
		elif self.size < BUF_SIZE: 
			times = 1
		elif self.size % BUF_SIZE == 0: 
			times = int(self.size / BUF_SIZE)
		else:
			self.size -= self.size % BUF_SIZE
			times = int(self.size / BUF_SIZE + 1)

		if bars:
			with alive_bar(times, bar='blocks', spinner='dots') as bar:
				with open(self.name, 'rb') as f:
					for _ in range(times):
						file_data = f.read(BUF_SIZE)
						sleep(SLEEP_VALUE)
						yield file_data
						bar()
		else:
			with open(self.name, 'rb') as f:
				for _ in range(times):
					file_data = f.read(BUF_SIZE)
					sleep(SLEEP_VALUE)
					yield file_data

	def update_data(self, sumtype, generated_data):
		"""Updates binary data to the sumtype's class."""
		for file_data in generated_data:
			self.hlist[sumtype].update(file_data)

	def checksum(self, sumtype):
		"""Compares file's sum with givensum."""
		if hexa_to_int(self.get_hashsum(sumtype)) == self.integer_sum:
			print(clr(f"{self.name}", "green"))
		else:
			print(clr(f"{self.name} X", "red"))


class Process(object):

	def __init__(self, files: list, sumtype=None):
		self.sumtype = sumtype
		# ´self.found´ and ´self.unfound´ store files,
		# depending on their existence or not.
		self.found = [f for f in files if f.existence is True]
		self.unfound = [f.name for f in files if f not in self.found]
		self.n_found = len(self.found)
		self.n_unfound = len(self.unfound)

	def checkfile(self, *, fid=None, fdata=None, bars=True, verbosity=True):
		"""Check and Compare the hash sum."""
		if not self.sumtype:
			print_error("Sumtype is Undefined!")
		elif not self.found and self.unfound:
			print_error(f"File not found: {self.unfound[0]!r}")
		elif not self.found and not self.unfound:
			print_error("Can't checksum without files!")
		else:
			fileid = self.found[0] if not fid else fid
			fileid.update_data(
				sumtype=self.sumtype, 
				generated_data=fileid.gen_data(bars=bars) if not fdata else fdata
			)
			print("\n -> ", end='')
			fileid.checksum(self.sumtype)
			if verbosity:
				print(f"Original Hash Sum:    {fileid.gsum!r}")
				print(f"Calculated Hash Sum:  {fileid.get_hashsum(self.sumtype)!r}")

	def show_sum(self, verbosity=True):
		"""Calculates and prints the file's hash sum"""
		if not self.sumtype:
			print_error("Sumtype is Undefined")
		elif self.found:
			with alive_bar(self.n_found, bar='blocks', spinner='dots') as bar:
				for fileid in self.found:
					fileid.update_data(self.sumtype, fileid.gen_data(bars=False))
					if verbosity:
						print(f"{fileid.get_hashsum(self.sumtype)} {fileid.name}")
					bar()

		self.print_unfound()

	def checkfile_plus(self, verbosity=False):
		"""Checks and compare the hash sums of more than one files."""
		if not self.sumtype:
			print_error("Sumtype is already undefined, you can determine it the sumtype be adding '--type sumtype' on the command call.")
		elif self.found:
			files_data = []
			with alive_bar(self.n_found, bar='blocks', spinner='dots') as bar:
				for fileid in self.found:
					if not verbosity:
						fileid.update_data(self.sumtype, fileid.gen_data(bars=False))
						fileid.checksum(self.sumtype)
					else: files_data.append(list(fileid.gen_data(bars=False)))
					bar()
			if verbosity: 
				for fileid, file_data in zip(self.found, files_data):
					self.checkfile(fid=fileid, fdata=file_data, bars=False)
		self.print_unfound()

	def totalcheck(self):
		"""Print all supported hash sums of one file."""
		if self.found:
			generated_datas = []
			with alive_bar(self.n_found, spinner='waves') as bar:
				print("Calculating Hashes")
				for fileid in self.found:
					generated_datas.append(list(fileid.gen_data(bars=False)))
					bar()
			print("\n")
			for n, fileid, generated_data in zip(range(self.n_found), self.found, generated_datas):
				if n > 0 and n < self.n_found:
					print("\n")		
				with alive_bar(len(fileid.hlist.keys()), spinner='waves') as bar:
					print("Getting '%s' Hash Sums" %fileid.name)
					for sumtype in fileid.hlist.keys():
						fileid.update_data(sumtype, generated_data)
						sleep(SLEEP_VALUE)
						bar()
				for sumtype in fileid.hlist.keys():
					print(f"{sumtype}sum: {fileid.get_hashsum(sumtype)} {fileid.name}")
		self.print_unfound()

	def print_unfound(self):
		"""Prints all files that were not found."""
		if self.unfound:
			print("\nThe files below were not found:")
			for filename in self.unfound:
				path = os.path.split(filename)
				directory, fname = path if path[0] else ('.', path[-1])
				print(f"  -> {fname!r} in {directory}/")
		else: pass

	def write(self, name=None):
		if self.found and self.sumtype:
			if not name:
				textfile = self.sumtype + 'sum.txt'
				ch = input(f"\nThe calculated hash sum will be saved on {textfile!r}, change name? [y|N]: ")
				if ch.lower() == 'y' or ch.lower() == 'yes':
					newname = input("Write the filename > ")
					if not newname.isspace():
						textfile = newname
			else: textfile = name
			with open(textfile, 'w') as txt:
				for fileid in self.found:
					txt.write(f"{fileid.get_hashsum(self.sumtype)} {fileid.name}\n")
			salutations(f"\n* File: {textfile!r} created!", time_sleep=0.064)
		else:
			print_error("Cannot write: no files were found!")

