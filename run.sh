PI="pi@192.168.1.38"
scp -r "output/art/painting.art" "${PI}:/home/pi/software/runtime/painting.art"
ssh $PI "python3 /home/pi/software/main.py /home/pi/software/runtime/painting.art"