""" This is a Superkaramba Timer/Stopwatch widget """
try:
    import karamba
except ImportError:
    print("karamba module not accessible")
import os
import re


# MyTime Class
##############################################################################
class MyTime(object):
    """ Class for representing a time object in the form
        hours:minutes:seconds
    """
    timepattern = re.compile( \
        "(?P<hour>[0-9]+):(?P<minute>[0-5][0-9]):(?P<second>[0-5][0-9])")

    def __init__(self, initvalue=None):
        """ Initialize Object to zero, or time described by the string
            initvalue, if given.
        """
        self._time = [0, 0, 0]
        if isinstance(initvalue, str):
            self.from_string(initvalue)

    def get_hours(self):
        """ Return hours as int """
        return self._time[0]

    def set_hours(self, value):
        """ Checks correctness of value and sets hour"""
        value = int(value)
        if value >= 0:
            self._time[0] = value
        else:
            raise ValueError("Number of hours must be positive")

    def get_minutes(self):
        """ Return minutes as int """
        return self._time[1]

    def set_minutes(self, value):
        """ Checks correctness of value and sets minute"""
        value = int(value)
        if 0 <= value <= 59:
            self._time[1] = value
        else:
            raise ValueError("Number of minutes must be between 0 and 59")
    
    def get_seconds(self):
        """ Return seconds as int """
        return self._time[2]
    
    def set_seconds(self, value):
        """ Checks correctness of value and sets second"""
        value = int(value)
        if 0 <= value <= 59:
            self._time[2] = value
        else:
            raise ValueError("Number of seconds must be between 0 and 59")

    def get_time(self):
        """ Return time in total number of seconds """
        return 3600 * self._time[0] + 60 * self._time[1] + self._time[2]

    def set_time(self, value):
        """ Sets time from total number of seconds """
        value = int(value)
        if value >= 0:
            self._time[0] = value / 3600
            self._time[1] = value % 60
            self._time[2] = (value % 3600) / 60
        else:
            raise ValueError("time bust be >= 0")
    
    def to_string(self):
        """ Return string representation of the time """
        return "%i:%02i:%02i" % (self.hours, self.minutes, self.seconds)

    def __str__(self):
        """ Return string representation of the time """
        return self.to_string()

    def from_string(self, timestr):
        """ Set time from string """
        timematch = self.timepattern.match(timestr)
        if timematch:
            self.hours = timematch.group('hour')
            self.minutes = timematch.group('minute')
            self.seconds = timematch.group('second')
   
    def increment(self, i=1):
        """ Increment time by i seconds """     
        hours, minutes, seconds = self.hours, self.minutes, self.seconds
        seconds += i
        if seconds >= 60:
            minutes += seconds / 60
            seconds = seconds % 60
        if minutes >= 60:
            hours += minutes / 60
            minutes = minutes % 60
        self.hours, self.minutes, self.seconds = hours, minutes, seconds
       
    def decrement(self, i=1):
        """ Decrement time by i seconds """
        hours, minutes, seconds = self.hours, self.minutes, self.seconds
        seconds -= i
        if seconds <= 0:
            minutes += seconds / 60
            seconds = seconds % 60
        if minutes <= 0:
            hours += minutes / 60
            minutes = minutes % 60
        self.hours, self.minutes, self.seconds = hours, minutes, seconds

    def copy(self):
        """ Create a new MyTime object that is initilized to the same time
            as self.
        """
        return MyTime(str(self))


    hours = property(get_hours, \
                     set_hours, \
                     doc = 'number of hours as int')
    minutes = property(get_minutes, \
                       set_minutes, \
                       doc = 'number of minutes as int')
    seconds = property(get_seconds, \
                       set_seconds,  \
                       doc = 'number of seconds as int' )
    time = property(get_time , \
                    set_time, \
                    doc='time in seconds')


# Initialization of global variables
##############################################################################
zerotime = MyTime("0:00:00")
alarmtime = MyTime("0:00:00")
curtime = zerotime.copy()
active = 0 # Start paused
raised_alarm = False
startButton = None
endButton = None
progressBar = None
curtimefile = None
done = None      # "done" image widget
hours = None     # these ...
minutes = None   # ... are the...
seconds = None   # widget texts




# Karamba handlers
##############################################################################

def initWidget(widget):
    """ This is called when your widget is initialized"""
    global startButton
    global endButton
    global progressBar
    global curtimefile
    global done      # "done" image widget
    global hours     # these ...
    global minutes   # ... are the...
    global seconds   # widget texts


    # initialize handlers to all meters
    hours = karamba.getThemeText(widget, "hours")
    seconds = karamba.getThemeText(widget, "seconds")
    minutes = karamba.getThemeText(widget, "minutes")
    progressBar = karamba.getThemeBar(widget, "progress")
    karamba.hideBar(widget, progressBar)
    startButton = karamba.getThemeImage(widget, "start")
    karamba.attachClickArea(widget, startButton, "", "", "")
    endButton = karamba.getThemeImage(widget, "end")
    karamba.attachClickArea(widget, endButton, "", "", "")
    done = karamba.getThemeImage(widget, "done")
    karamba.attachClickArea(widget, done, "", "", "")

    # read data from config file
    zerotime_str = str(karamba.readConfigEntry(widget, "zerotime"))
    print "zerotime from config: %s" % zerotime_str
    zerotime.from_string(zerotime_str)
    alarmtime_str= str(karamba.readConfigEntry(widget, "alarmtime"))
    print "alarmtime from config: %s" % alarmtime_str
    alarmtime.from_string(alarmtime_str)


    # set time from last used time
    curtimefile =  os.path.join(os.environ['HOME'], \
                                '.superkaramba', \
                                'stoptimer', \
                                'curtime')
    if os.path.isfile(curtimefile):
        curtimefh = open(curtimefile)
        curtimestring = curtimefh.read()
        curtime.from_string(curtimestring)
        curtimefh.close()
    else:
        if not os.path.isdir( \
         os.path.join(os.environ['HOME'], '.superkaramba')):
            os.mkdir(os.path.join(os.environ['HOME'], '.superkaramba'))
        if not os.path.isdir( \
        os.path.join(os.environ['HOME'], '.superkaramba', 'stoptimer')):
            os.mkdir(os.path.join( \
                     os.environ['HOME'], '.superkaramba', 'stoptimer'))

    showTime(widget, curtime)



def widgetUpdated(widget):
    """ This is called every time the widget is updated.
        The update interval is specified in the .theme file
    """
    global active
    global raised_alarm
    stopwatchmode = (zerotime.time < alarmtime.time)

    if active == 1:
        # increment/decrement, depending on mode
        if stopwatchmode:
            stepmethod = curtime.increment
        else:
            stepmethod = curtime.decrement
        try:
            stepmethod()
        except ValueError:
            # stop, instead of going below zero
            print "caught time going below zero"
            meterClicked(widget, endButton, 1)

        # reflect new time in GUI
        showTime(widget, curtime)
        if stopwatchmode:
            karamba.setBarValue(widget, progressBar, curtime.time)
        else:
            karamba.setBarValue(widget, progressBar, \
                                alarmtime.time + zerotime.time - curtime.time)
        karamba.redrawWidget(widget)

        # write current time to file
        curtimefh = open(curtimefile, "w")
        curtimefh.write(str(curtime))
        curtimefh.close()

        # alarm?
        if not raised_alarm:
            if (stopwatchmode and (curtime.time >= alarmtime.time)) \
            or (not stopwatchmode and (curtime.time <= alarmtime.time)):
                karamba.showImage(widget, done)
                karamba.redrawWidget(widget)
                alarm(widget)
                raised_alarm = True


def meterClicked(widget, meter, button):
    """ This gets called when a meter (image, text, etc) is clicked.
        NOTE you must use attachClickArea() to make a meter
        clickable.
          widget = reference to your theme
          meter = the meter clicked
          button = the button clicked
    """
    global active
    global raised_alarm
    global curtime

    if meter == startButton:
        if active == 0:
            print "startButton"
            karamba.showBar(widget, progressBar)
            if zerotime.time < alarmtime.time:
                karamba.setBarMinMax(widget, progressBar, \
                                     zerotime.time, alarmtime.time)
            else:
                karamba.setBarMinMax(widget, progressBar, \
                                     alarmtime.time, zerotime.time)
            karamba.setBarValue(widget, progressBar, curtime.time)
            karamba.hideImage(widget, done)
            karamba.setImagePath(widget, startButton, "img/startpause.png")
            karamba.setImagePath(widget, endButton, "img/stoppause.png")
            active = 1
        else:
            print "startButton (Pause)"
            karamba.setImagePath(widget, startButton, "img/start.png")
            karamba.setImagePath(widget, endButton, "img/stop.png")
            active = 0
    elif meter == endButton:
        if active == 0:
            print "endButton"
            curtime = zerotime.copy()
            showTime(widget, curtime)
            karamba.showImage(widget, done)
            karamba.hideBar(widget, progressBar)
            curtimefh = open(curtimefile, "w")
            curtimefh.write(str(curtime))
            curtimefh.close()
            karamba.setImagePath(widget, startButton, "img/start.png")
            karamba.setImagePath(widget, endButton, "img/stop.png")
            raised_alarm = False
        else:
            print "endButton (Pause)"
            karamba.setImagePath(widget, startButton, "img/start.png")
            karamba.setImagePath(widget, endButton, "img/stop.png")
            active = 0
    elif meter == done:
        print "done"
        alarmtime.from_string(getValue(widget, "Alarm Time", str(alarmtime)))
        karamba.writeConfigEntry(widget, "alarmtime", str(alarmtime))
    else:
        print "anotherbutton"


def widgetClicked(widget, x, y, button):
    "Clicking the widget in the top area allows you to set the zerotime """
    if y < 70 and active == 0:
        print "clicked widget"
        read_zerotime(widget)





# Helper Functions
#############################################################################

def alarm(widget):
    """ Raise an alarm """
    print "ALARM !"
    #alarm_command = ["play","/home/goerz/.sounds/blip.wav"]
    #karamba.executeInteractive(widget, alarm_command)

def showTime(widget, timeobject):
    """ Update the time widgets to show the time defined in the timeobject """
    karamba.changeText(widget, hours, "%i" % timeobject.hours)
    karamba.changeText(widget, minutes, "%02i" % timeobject.minutes)
    karamba.changeText(widget, seconds, "%02i" % timeobject.seconds)

def getValue(widget, name, cur_value):
    """ Get a value interactively """
    arg = 'kdialog --inputbox \"'+name+'\" \"'+str(cur_value)+'\" '
    return os.popen(arg, "r").read()

def read_zerotime(widget):
    global curtime
    print "read_zerotime"
    zerotime.from_string(getValue(widget, "Initial Time", str(zerotime)))
    karamba.writeConfigEntry(widget, "zerotime", str(zerotime))
    curtime = zerotime.copy()
    showTime(widget, curtime)

print "Extension for widget Timer loaded!"

