import telnetlib
import csv
import time
import pandas as pd

class Scanner:

    def __init__(self, hostname='127.0.0.1', port=7356, wait_time=5, signal_strength=-55):
        self.host = hostname
        self.port = port
        self.wait_time = wait_time
        self.signal_strength = signal_strength
        self.freqs = None
        self.mode_map = {'Narrow FM' : 'FM',
                         'Demod Off' : 'OFF',
                         'Raw I/Q'   : 'RAW',
                         'AM-Sync'   : 'AMS',
                         'AM'        : 'AM',
                         'USB'       : 'USB',
                         'LSB'       : 'LSB',
                         'WFM (mono)': 'WFM',
                         'WFM (stereo)' : 'WFM_ST',
                         'WFM (oirt)': 'WFM_ST_OIRT',
                         'CW-L'      : 'CWL',
                         'CW-U'      : 'CWU'}
        # M - Set demodulator mode (OFF, RAW, AM, FM, WFM, WFM_ST,
        # WFM_ST_OIRT, LSB, USB, CW, CWL, CWU)
        self.block_list = pd.Series(dtype=bool) # list of lists to block a small window of birdies and other interference
        self.block_radius = 10000 # +/- Hz (same 2*bw as NFM)

    def _add_new_block(self, freq):
        '''
        Add an interval (freq-self.block_radius, freq+self.block_radius)
        '''
        radius = self.block_radius
        block_index = pd.IntervalIndex.from_tuples([(freq-radius, freq+radius)], closed='both')
        block_ser = pd.Series(True, index=block_index)
        self.block_list = self.block_list.append(block_ser)

    def _is_blocked(self, freq):
        try:
            blocks = self.block_list.loc[freq]
            if blocks: # only a single block interval with this freq
                return blocks
        except KeyError: # not blocked
            return False
        except ValueError: # means blocked in more than one interval
            return any(blocks)
        except:
            return False

    def _update(self, msg):
        """
        update the frequency/mode GQRX is listening to
        """
        try:
            tn = telnetlib.Telnet(self.host, self.port)
        except Exception as e: 
            print("Error connecting to " + self.host + ":" + str(self.port) + "\n\t" + str(e))
            exit()
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
                try:
                    if self.freqs[freq]['tag'].lower() == 'skip':
                        print(f"Skipping {freq}: {self.freqs[freq]['name']}")
                        continue
                except KeyError:
                    pass
                self._set_freq(freq)
                self._set_mode(self.freqs[freq]['mode'])
                self._set_squelch(self.signal_strength)
                time.sleep(0.35)
                level = float(self._get_level())
                if level >= self.signal_strength:
                    last_sig_time = pd.Timestamp.now()
                    while True:
                        if float(self._get_level()) >= self.signal_strength:
                            last_sig_time = pd.Timestamp.now()

                        if pd.Timestamp.now() - last_sig_time > pd.Timedelta(f"{self.wait_time}S"):
                            break

    def scan_range(self, minfreq, maxfreq, mode, step=500, save_path=None):
        """
        Scan a range of frequencies

        :param minfreq: lower frequency (MHz)
        :param maxfreq: upper frequency (MHz)
        :param mode: mode to scan in
        :param step: step size (Hz)
        :param save_path: (optional) a txt file to save the active frequencies to
        :return: none

        """
        minfreq = int(float(minfreq) * 1e6)
        maxfreq = int(float(maxfreq) * 1e6)

        if save_path is not None:
            writer = open(save_path, 'wa')

        else:
            freq = minfreq
            while(1):

                if freq <= maxfreq:

                    self._set_freq(freq)
                    self._set_mode(mode)
                    self._set_squelch(self.signal_strength)
                    time.sleep(0.15)
                    if float(self._get_level()) >= self.signal_strength:
                        if self._is_blocked(freq):
                            freq = freq + step
                            continue
                        timenow = pd.Timestamp.now()
                        print(timenow, freq)
                        if save_path is not None:
                            writer.write(f"{timenow}:  {freq}")
                        while float(self._get_level()) >= self.signal_strength:
                            key = input()
                            if key == '':
                                freq = freq + step
                                break
                            elif 'block' in key.lower():
                                self._add_new_block(freq)
                                freq = freq + step
                                break
                            else:
                                pass

                    else:
                        freq = freq + step
                else:
                    freq = minfreq

    def read_bookmarks(self, file_path):
    	'''
		Read the bookmarks associated with gqrx
		to fit better with the gqrx application
        In Linux systems the file is in ~/.config/gqrx/bookmarks.csv
    	'''
    	self.freqs = {}
    	with open(file_path, 'r') as csvfile:
    		freq_block = False # did we hit the freqs yet?
    		line = csvfile.readline()

    		while True:
	    		if 'Frequency' in line:
	    			freq_block = True
	    			break

    			# throw away the color scheme section
    			line = csvfile.readline()

    		freq_lines = []
    		while line:
    			line = csvfile.readline()
    			freq_lines.append(line.split(';'))

    	freq_df = pd.DataFrame(freq_lines, columns=['Frequency', 'Name', 'Modulation', 'Bandwidth', 'Tags'])

    	# as of now (2022), there isn't a way to set bandwidth (I tried to use B and b to no avail) so we dont save that info
    	for row in freq_df.itertuples():
    		# [1] = freq
    		# [2] = name
    		# [3] = mod
            try:
                self.freqs[int(row[1])] = {'mode': self.mode_map[row[3].strip()], 'name':row[2].strip(), 'tag': row[5].strip()}
            except AttributeError:
                pass


    def load(self, freq_csv='freq.csv'):
        """
        read the csv file with the frequencies & modes
        in it into a dict{} where keys are the freq and
        the value is a dict with the mode and a tag
        csv is in the format 
            freq (MHz), mode, name
        """
        self.freqs = {}
        with open(freq_csv, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = ',')
            for row in reader:
                freq = int(float(row[0])*1e6)                                 # Input is in mhz
                freq = int(freq)                                        	  # converted to hz
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
    scanner = Scanner(signal_strength=-60)
    scanner.load()
    scanner.scan()