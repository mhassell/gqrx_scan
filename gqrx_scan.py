import telnetlib
import csv
import time

class Scanner:

	def __init__(self, hostname='127.0.0.1', port=7356, directory='/', waitTime=8, signalStrength=-12):
		self.host = hostname
		self.port = port
		self.directory = directory
		self.waitTime = waitTime
		self.signalStrength = signalStrength

	def _update(self, msg):
		"""
		update the frequency/mode GQRX is listening to
		"""
		tn = telnetlib.Telnet(self.host, self.port)
		tn.write(('%s\n' % msg).encode('ascii'))
		response = tn.read_some().decode('ascii').strip()
		tn.write('c\n'.encode('ascii'))
		return response

	def scan(self):
		"""
		loop over the frequencies in the list, 
		and stop if the frequency is active (signal strength is high enough)
		"""
		while(1):
			for freq in self.freqs.keys():
				self._set_freq(freq)
				self._set_mode(self.freqs[freq]['mode'])
				self._set_squelch(self.signalStrength)
				time.sleep(0.5)
				if float(self._get_level()) >= self.signalStrength:
					timenow = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
					print timenow, freq, self.freqs[freq]['tag']
					while float(self._get_level()) >= self.signalStrength:
						time.sleep(self.waitTime)

	def scan_range(self, minfreq, maxfreq, mode, save = None):
		"""
		Scan a range of frequencies

		:param minfreq: lower frequency
		:param maxfreq: upper frequency
		:param mode: mode to scan in
		:param save: (optional) a txt file to save the active frequencies to
		:return: none

		"""
		if save is not None:
			pass

		else:
			freq = minfreq
			while(1):
				if freq <= maxfreq:
					self._set_freq(freq)
					self._set_mode(mode)
					self._set_squelch(self.signalStrength)
					time.sleep(0.5)
					if float(self._get_level()) >= self.signalStrength:
						timenow = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
						print timenow, freq
						while float(self._get_level()) >= self.signalStrength:
							time.sleep(self.waitTime)
					else:
						freq = freq + 100
				else:
					freq = minfreq


		pass

   	def load(self, freq_csv='freq.csv'):
   		"""
   		read the csv file with the frequencies & modes
		in it into a dict{} where keys are the freq and
		the value is a dict with the mode and a tag
   		"""
   		self.freqs = {}
   		with open(freq_csv, 'r') as csvfile:
   			reader = csv.reader(csvfile, delimiter = ',')
   			for row in reader:
   				freq = str(float(row[0])*1e5)	    					# 1e5 isn't good
   				freq = int(freq.replace('.', ''))   					# converted to hz
				if len(row) == 2:
					self.freqs[freq] = {'mode': row[1], 'tag': None}
				elif len(row) == 3:
   					self.freqs[freq] = {'mode' : row[1], 'tag': row[2]}     # add the freq to the dict as a key and the mode as the value

   	def _set_freq(self, freq):
   		return self._update("F %s" % freq)

   	def _set_mode(self, mode):
   		return self._update("M %s" % mode)

	def _set_squelch(self, sql):
		return self._update("L SQL %s" % sql)

   	def _get_level(self):
   		return self._update("l")

	def _get_mode(self):
		return self._update('m')

if __name__ == "__main__":
	scanner = Scanner()
	scanner.load()
	scanner.scan()
