import telnetlib
import csv
import time

class Scanner:

	def __init__(self, hostname='127.0.0.1', port=7356, directory='/', waitTime=5, signalStrength=-15):
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
		loop over the frequencies in the list, and stop if the frequency is active (signal strength is high enough)
		"""
		while(1):
			for freq in self.freqs.keys():
				self._set_freq(freq)
				self._set_mode(self.freqs[freq])
				time.sleep(0.2)
				if float(self._get_level()) >= self.signalStrength:
					print freq
					while float(self._get_level()) >= self.signalStrength:
						time.sleep(self.waitTime)


   	def load(self):
   		"""
   		read the csv file with the frequencies & modes in it into a dict{} where keys are the freq and values are the mode
   		"""
   		self.freqs = {}
   		with open('freq.csv','r') as csvfile:
   			reader = csv.reader(csvfile, delimiter = ',')
   			for row in reader:
   				freq = str(float(row[0])*1e5)		# 1e5 isn't good
   				freq = int(freq.replace('.', '')) 	# converted to hz
   				self.freqs[freq] = row[1]     		# add the freq to the dict as a key and the mode as the value


   	def _set_freq(self, freq):
   		return self._update("F %s" % freq)

   	def _set_mode(self, mode):
   		return self._update("M %s" % mode)

   	def _get_level(self):
   		return self._update("l")

if __name__ == "__main__":
	scanner = Scanner()
	scanner.load()
	scanner.scan()
