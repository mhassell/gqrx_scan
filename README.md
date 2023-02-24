# gqrx_scan

A scanner to interface with GQRX, based on the remote control tool https://github.com/marmelo/gqrx-remote  

Loops over a list of frequencies in a csv and listens for activity.  

Usage: 

Import the module, and make a scanner instance:

	scanner = gqrx_scan.Scanner(hostname='127.0.0.1', port=7356, wait_time=5, signal_strength=-55)

These are the default arguments in the constructor, which you can modify as you need.  The hostname and port are where the scanner connects to GQRX.  The directory is where you've saved a csv file with the frequencies you wish to scan.  The wait_time is how long the scanner waits after a signal drops below the threshold before continuing scanning.  This is useful if you have dispatch tones before a voice dispatch, for example.   The signal_strength field is the strength below which signals are ignored (squelch).

Once you have a scanner object, call 

	scanner.load(freq='freq.csv') 

to import the csv into the scanner, and then run 

	scanner.scan()

The csv file should be of the format

	freq, mode, name

where the frequency is in MHz.  Specify the mode according to one of the modes in the table below.  On the left the is name of the mode, on the right is what you enter in the csv file.

	'Narrow FM' : 'FM'
	'Demod Off' : 'OFF'
	'Raw I/Q'   : 'RAW'
	'AM-Sync'   : 'AMS'
	'AM'        : 'AM'
	'USB'       : 'USB'
	'LSB'       : 'LSB'
	'WFM (mono)': 'WFM'
	'WFM (stereo)' : 'WFM_ST'
	'WFM (oirt)': 'WFM_ST_OIRT'
	'CW-L'      : 'CWL'
	'CW-U'      : 'CWU'

If you store bookmarks in GQRX, you can use those as input to the scanner as well:

	scanner.read_bookmarks(path-to-bookmarks)

and again call the scan() method.   The bookmarks are stored (at least for me on Linux) in \~/.config/gqrx/bookmarks.csv

To scan a range of frequencies with a given mode, we can instead use the scan_range method as follows:

    scanner.scan_range(minfreq, maxfreq, mode, step=500, save=None)

This loops continuously from minfreq to maxfreq with a step size of step (defaults to 500 Hz) and stops 
when there is a transmission.  In the future I'd like to add a save option to write active frequencies to a file for later review.
As an example, we can scan the US FM broadcast band by way of the command

    scanner.scan_range(88.0, 108.0, 'WFM_ST', step=100000)
 
This will loop over the FM broadcast bands and stop on the first active station.

There's a sample csv file for the format the scanner expects.  The first column is the frequency, the second is the mode, and the third is an optional tag for the channel.  
This is displayed in the terminal, along with the time and frequency, when a transmission occurs.

Make sure you have enabled remote connections in GQRX.

This is still  in it's early phases, and there's a lot of cool features to add.  If anyone would like to contribute, submit a pull request!

TBD:

1. GUI

2. Ability to add/delete frequencies in the GUI

3. Set squelch/signal_strength for each channel

4. Timeout for scan_range (so as not to get stuck on a birdie or a continuous broadcast)

5. Logging for the scan_range function to find interesting frequencies automatically

6. Interface with automatic recording of a given frequency (or set of freqs) and save the audio and timestamp like gqrx does
