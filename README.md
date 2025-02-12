# gqrx_scan

A scanner to interface with GQRX, based on the remote control tool [gqrx-remote](https://github.com/marmelo/gqrx-remote)

Loops over a list of frequencies in a csv and listens for activity.  

Usage:

Import the module, and make a scanner instance:

	scanner = gqrx_scan.Scanner(hostname='127.0.0.1', port=7356, wait_time=5, signal_strength=-55)

These are the default arguments in the constructor, which you can modify as you need.  The hostname and port are where the scanner connects to GQRX.  The wait_time is how long the scanner waits after a signal drops below the threshold before continuing scanning.  This is useful if you have dispatch tones before a voice dispatch, for example.   The signal_strength field is the strength below which signals are ignored.

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

The mode, frequency, and optional tag are displayed in the terminal, along with the time and frequency, when a transmission occurs.

If you store bookmarks in GQRX, you can use those as input to the scanner as well:

	scanner.read_bookmarks(path-to-bookmarks)

and again call the scan() method.   The bookmarks are stored in `\~/.config/gqrx/bookmarks.csv` on Linux systems.   Sometimes it is worth skipping some bookmarked frequencies.  If you change the "Tag" for a bookmark to "skip," the scanner will ignore that frequency.  If you change/add/remove a tag while running the scanner, you need to call `scanner.read_bookmarks(path-to-bookmarks)` again to update the bookmarks.

There's also a way to use the bookmarks to choose what you do and do not want to scan.  If we pass a list of strings to `scan`, the `scan` command will check if the Tag of each bookmark is in the list.  If so, it tunes to that channel, otherwise it skips it.  We can assign some frequencies to be in a group called 'Ham' and other frequencies to be in a group called 'Aircraft'. A call of `scan(['Ham'])` will only scan the frequencies with the 'Ham' tag and will skip the 'Aircraft' tag.  If we call `scan()` without arguments, it will scan all of the frequencies except for those marked 'skip'.  We can also call `scan(['Ham', 'Aircraft'])` to specify more than one tag to scan.

To scan a range of frequencies with a given mode, we can instead use the `scan_range` method as follows:

    scanner.scan_range(minfreq, maxfreq, mode, step=500, save=None)

This loops continuously from minfreq to maxfreq with a step size of step (defaults to 500 Hz) and stops when there is a transmission.
As an example, we can scan the US FM broadcast band by way of the command

    scanner.scan_range(88.0, 108.0, 'WFM_ST', step=100000)
 
This will loop over the FM broadcast bands and stop on the first active station.  While scanning over a range we may hit interference we do not want to keep waiting on.  We can either press Enter and we will increment to the next frequency (current frequency + step) or we can type "block" in the command line. The block command will enter the current frequency and a window around it into an ignore list.  The next time we pass near that frequency, we will not stop for any signals.  The block command creates an interval of the form `[freq-eps, freq+2*B]` around the frequency.  By default B is 5KHz, which will block an NFM signal.  eps is 1KHz to account for squelch's impact on when the signal if first detected.  The block intervals are not saved for future usage.

Another feature is to monitor a list of frequencies for recording purposes.  Modify the `record_freqs.csv` file to have the frequency in Hz and the mode in one row for each channel you want to record.  Then run the recording scanner as follows:

```
from gqrx_scan import Scanner
sc = Scanner(signal_strength=-60)
sc.set_record_list("record_freqs.csv")
sc.listen_and_record(time_limit=10)
```

With a scanner instance, we set the path to the recording frequencies via `set_record_list`.  We then call `listen_and_record`. The `time_limit` value is how many seconds we will continue recording after the signal drops below the `signal_strength` threshold.  If no `time_limit` value is provided then the default is 10 seconds. Sometimes it makes sense to extend this based on the nature of what is being recorded. When we encounter a signal on the `record_freqs.csv` list, it begins recording the audio output to a .wav file.  If the sound from the file is clipping, then adjust the gain down on the audio panel in GQRX (Crtl+A). If you interrupt the scanner while recording, the recording will be stopped.

Another option for the listen_and_record method is to set the audio flag to false (it defaults to true): `listen_and_record(audio=False)`.  This will capture IQ data instead of audio data.  Beware! IQ data is generally much larger than audio data, so a lengthy recording or a recording from a device with a large bandwith will take up a lot of disk space.


Make sure you have enabled remote connections in GQRX.

If you would like to contribute, submit a pull request!

TBD:

1. GUI?

2. Ability to add/delete frequencies in the GUI

3. Set `signal_strength` for each channel

4. Timeout for `scan_range` (so as not to get stuck on a birdie or a continuous broadcast)

5. Pause scanning from command line

6. Figure out why the sleep commands are needed.  I opened an [issue](https://github.com/mhassell/gqrx_scan/issues/6) to explore this.  In my own trials it seems there is a delay of when we change frequency and mode, and then fetch the signal level.  We need a 0.75s delay to capture the signal level for the channel we tuned to.  Otherwise, we either get a value that is not representative of the signal and scan in a loop forever, or we get the signal level for a frequency that was set a few steps ago.  I am curious if other people who wrote scanner utilities, eg, [neural75s](https://github.com/neural75/gqrx-scanner) scanner.  This one does something interesting -- it scans past a channel with signal, and then backpedals iteratively until it finds the peak of the signal.  I am curious if this Newton's-method-like approach is to overcome this delay between detecting a signal and registering the signal strength through telnet.
