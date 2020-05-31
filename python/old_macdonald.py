import gpiozero
import time

buzzer = gpiozero.TonalBuzzer(2)

l1 = ["G4", "G4", "G4", "D4", "E4", "E4", "D4"]
l2 = ["B4", "B4", "A4", "A4", "G4"]
l3 = ["D4", "G4", "G4", "G4", "D4", "E4", "E4", "D4"]

song = [l1, l2, l3, l2]

for line in song:
    for note in line:
        buzzer.play(note)
        time.sleep(0.4)
        buzzer.stop()
        time.sleep(0.1)
    time.sleep(0.2)

