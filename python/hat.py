import gpiozero
import time

buzzer = gpiozero.TonalBuzzer(2)

green = gpiozero.PWMLED(14)
yellow = gpiozero.PWMLED(18)
orange = gpiozero.PWMLED(23)
red = gpiozero.PWMLED(19)
blue = gpiozero.PWMLED(8)

blue.pulse(fade_in_time=5, fade_out_time=5)

while True:
	for i in range(16):
		green.value =  bool(i & 0b00000001)
		yellow.value = bool(i & 0b00000010)
		orange.value = bool(i & 0b00000100)
		red.value =    bool(i & 0b00001000)

		# buzzer.value = bool(i & 0b00000010)

		print("G: {0}  Y: {1}  O: {2}  R: {3}  B: {4}".format(green.value, yellow.value, orange.value, red.value, blue.value))

		time.sleep(0.5)
