import rtmidi, os, plistlib, inspect

midiin = rtmidi.RtMidiIn()


class MIDIMapping(object):
	def __init__(self, controllerName):
		self.controllerName = controllerName.replace('/', '_')
		self.mapping = plistlib.readPlist(os.path.join(os.path.dirname(__file__), 'mappings', self.controllerName + '.plist'))
		self.methods = {}
		midiin.openPort(0)
		self.reverseMapping = inv_map = {v: k for k, v in self.mapping.iteritems()}

	def start(self):
		while True:
			m = midiin.getMessage(250) # some timeout in ms
			if m:
				self.message(m)

	def __repr__(self):
		return '<MidiMapping "%s">' % self.controllerName

	def map(self, key, method):
		self.methods[key] = method

	def message(self, midi):
		if midi.isNoteOn():
			key = 'ON,%s' % midi.getMidiNoteName(midi.getNoteNumber())
			value = midi.getVelocity()
		elif midi.isNoteOff():
			key = 'OFF,%s' % midi.getMidiNoteName(midi.getNoteNumber())
			value = 0
		elif midi.isController():
			key = 'CONTROLLER,%s' % midi.getControllerNumber()
			value = midi.getControllerValue()

		if key in self.reverseMapping:
			mappedKey = self.reverseMapping[key]
			if mappedKey in self.methods:

				args = inspect.getargspec(self.methods[mappedKey]).args
				if args == ['value']:
					self.methods[mappedKey].__call__(value)
				elif args == ['key', 'value']:
					self.methods[mappedKey].__call__(mappedKey, value)
				else:
					raise TypeError('Method %s doesnt have (value) or (key, value) interface: %s' % (self.methods[mappedKey].__name__, args))
			else:
				print('Pressed: %s' % mappedKey)
		else:
			print(key)


def on(value):
	print 'on, %s' % value

if __name__ == '__main__':
	mm = MIDIMapping(midiin.getPortName(0))
	mm.map('play', on)
	mm.start()