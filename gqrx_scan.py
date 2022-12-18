import telnetlib
import csv
import time

class Scanner:

    def __init__(self, hostname='127.0.0.1', port=7356, directory='/', wait_time=5, signal_strength=-20):
        self.host = hostname
        self.port = port
        self.directory = directory
        self.wait_time = wait_time
        self.signal_strength = signal_strength

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
                self._set_freq(freq)
                self._set_mode(self.freqs[freq]['mode'])
                self._set_squelch(self.signal_strength)
                time.sleep(1)
                if float(self._get_level()) >= self.signal_strength:
                    timenow = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
                    print(timenow, freq, self.freqs[freq]['tag'])
                    while float(self._get_level()) >= self.signal_strength:
                        time.sleep(self.wait_time)

    def scan_range(self, minfreq, maxfreq, mode, step=500, save = None):
        """
        Scan a range of frequencies

        :param minfreq: lower frequency
        :param maxfreq: upper frequency
        :param mode: mode to scan in
        :param save: (optional) a txt file to save the active frequencies to
        :return: none

        """
        minfreq = str(float(minfreq) * 1e5)
        minfreq = int(minfreq.replace('.', ''))

        maxfreq = str(float(maxfreq) * 1e5)
        maxfreq = int(maxfreq.replace('.', ''))

        if save is not None:
            pass

        else:
            freq = minfreq
            while(1):
                if freq <= maxfreq:

                    self._set_freq(freq)
                    self._set_mode(mode)
                    self._set_squelch(self.signal_strength)
                    time.sleep(0.5)
                    if float(self._get_level()) >= self.signal_strength:
                        timenow = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
                        print(timenow, freq)
                        print("Press enter to continue scanning")
                        while float(self._get_level()) >= self.signal_strength:
                            key = raw_input()
                            if key == '':
                                freq = freq + step
                                break

                    else:
                        freq = freq + step
                else:
                    freq = minfreq

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
                freq = str(int(float(row[0])*1e6))                      # 1e5 isn't good
                freq = int(freq.replace('.', ''))                       # converted to hz
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
