# gqrx_scan

A scanner to interface with GQRX, based on the remote control tool https://github.com/marmelo/gqrx-remote  

Simply loops over a list of frequencies in a csv and listens for activity.  

Usage: 

Simply import the module, and make a scanner instance:

	scanner = gqrx_scan.Scanner(hostname='127.0.0.1', port=7356, directory='/', waitTime=5, signalStrength=-15)

These are the default arguments in the constructor, which you can modify as you need.  The hostname and port are where the scanner conneects to GQRX.  The directory is where you've saved a csv file with the frequencies you wish to scan.  The waitTime is how long the scanner waits after a signal drops below the threshold before continuing scanning.  This is useful if you have dispatch tones before a voice dispatch, for example.   The signalStrength field is the strength below which signals are ignored.

Once you have a scanner object, call 

	scanner.load() 

to import the csv into the scanner, and then run 

	scanner.scan()

There's a sample csv file for the format the scanner expects.  The first column is the frequency, and the second is the mode.  

Make sure you have enabled remote connections in GQRX.

This is still  in it's early phases, and there's a lot of cool features to add.  If anyone would like to contribute, submit a pull request!

TBD:

1. GUI

2. Ability to add/delete frequencies in the GUI

3. Set squelch/signalStrength for each channel

4. Include tags for each channel
