# NeoAmpel Paul Sattler

#Eine Ampel mit NeoPixel, Python, Kotlin und JS

#setup start on boot

#set raspi-config 3Boot Options B1 Desktop/CLI B2 Console Autologin

#bash

sudo nano /etc/rc.local

#end bash

#edit file

...

(sudo) ifconfig [eth0/Other Adapter] up

sleep 10 

(sudo) python[2/3] /path/websocket.py & 

#& <- for loop programms              ^

exit 0

#end edit file

#bash 

sudo chmod +r+w+x /etc/rc.local

sudo reboot

#end bash

#setup apache2 webserver

sudo cp /path/Ampel.css /var/www/html/Ampel.css

sudo cp /path/index.php /var/www/html/index.html

sudo service apache[2] restart 


#edit ip & port in index.html -> Server ip! IP must be static. 

#edit ip & port in websocket.py -> Server ip! IP must be static.

#edit ip & port in Android apk. MainAktivit.kt

#Example: IP:192.168.188.24 Port:666


#Setup GPIO pins. 

#GRND eq PIN6 

#DATA eq PIN12

#connect RASPI GRND to Supply GRND
