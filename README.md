Notice
=======

The project has moved [here](https://github.com/Double-Fine-Game-Club/game-club-player).
This repository will no longer be updated.

DF Game Club Past Sessions Player
==================================

What is it?
------------
A tool for playing back past sessions of the [Double Fine Game Club][1],
along with the IRC chat transcripts.

How does it work?
------------------
1. Create a new entry in the configuration file for the game session
   you want to watch (if it's not already there, of course).
2. Run the Python script with the configuration file as an argument
   (or run it without arguments to use the default name, `config.ini`).
3. Upload the newly created `.html` and `.json` files,
   as well as the `javascript`, `styles`, `fonts` and `images` directories,
   to a web server (this is *very* important).
4. Open the web page.
5. Click the "Click to play/pause" link.
6. Enjoy!

Limitations
------------
Currently, it's not possible to control playback apart from
pausing and resuming. Using the playback controls on the video player
will break the synchronization between the video and the message stream.

Technical details
------------------
### Dependencies
- [Python 3]
- [Beautiful Soup 4]

### Configuration file structure
The config consists of several **sections**, each section representing
a particular Game Club session. In each section are several **key-value**
pairs that customize how each session is treated. If you have multiple
sections that share some of their parameters, you can put them
in the `DEFAULT` section to avoid repetition.

See the `config.ini` file in this repository for examples.

#### pastebin_url
URL pointing to the IRC log on [Pastebin].

#### twitch_url
URL pointing to the stream on [Twitch].

#### regex
Each line of the IRC log will be matched against this regular expression
in order to extract it's components. The expression must contain the following
**named capturing groups**:

- `timestamp`   - for capturing the timestamp of the message.
- `username`    - for capturing the username of the person
                  that sent the message.
- `message`     - for capturing the body of the message.
- `service`     - for capturing IRC notifications, such as people
                  entering or leaving the room and nickname changes.

If the matched expression's `username` group is empty, it is considered
to be a service message. Therefore, avoid splitting such messages
into a `username` group and a `service` group.

- Regular messages must contain *only* the `timestamp`, `username`
  and `message` groups.
- Service messages must contain only the `timestamp` and `service` groups.

For assistance with constructing regular expressions, visit: [regex101.com][2].

#### timestamp_format
Each timestamp in the IRC log will be run against this format string
for conversion into a `datetime` object.
See the [Python documentation][3] for help on `datetime` format strings.

#### video_timestamp
The time at which to begin playing the stream.
Must match the `timestamp_format`.

#### ignore_lines
A comma separated list of line numbers to ignore in the IRC log.

#### message_format
Format string for regular IRC messages.
Must contain keyword arguments `username` and `message`.
See the [Python documentation][4] for help on format strings.

#### service_format
Same as `message_format`. Must contain the `service` keyword argument.

Licensing
----------
See the individual files in this repository for licensing information.
Or you can see the `LICENSE` file if you like pointers.

Acknowledgements
-----------------
- [Cheeseness] for the original HTML5 and CSS3.
- Janne Enberg (aka [lietu]) for the original JavaScript.

[1]: http://double-fine-game-club.github.io/
[2]: http://regex101.com/
[3]: http://docs.python.org/3.3/library/datetime.html#strftime-and-strptime-behavior
[4]: http://docs.python.org/3.3/library/string.html#format-string-syntax
[Pastebin]: http://pastebin.com/
[Twitch]: http://twitch.tv/
[Python 3]: http://python.org/
[Beautiful Soup 4]: http://www.crummy.com/software/BeautifulSoup/
[Cheeseness]: http://jbushproductions.com
[lietu]: https://github.com/lietu
