#!/usr/bin/env python

import csv
import RPi.GPIO as GPIO
import time
import smtplib
from subprocess import call
from mfrc522 import SimpleMFRC522
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydub import AudioSegment
from pydub.playback import play

def number_in_file(number, filepath):
    with open(filepath, 'r') as f:
        for line in f:
            if str(number) in line:
                return True
    return False

reader = SimpleMFRC522()

try:
	id, text = reader.read()
	print(id)
	print(text)

	filepath = 'rfid.csv'
	number = id

	if number_in_file(number, filepath):
		print(f'{number} szerepel az adatbazisban: {filepath}')
		song=AudioSegment.from_wav('/home/pi/edkb-rfid/belepes_engedelyezvex.wav')
		play(song)
	else:
		print(f'{number} nem szerepel az adatbazisban: {filepath}')
		song=AudioSegment.from_wav('/home/pi/edkb-rfid/uj_rfid_regx.wav')
		play(song)
		fenykep_nev = str(id) + '.jpg'
		cmd = 'raspistill -t 500 -w 1024 -h 768 -o /home/pi/edkb-rfid/pics/' + fenykep_nev
		call ([cmd], shell=True)
		print('Fenykep kesz,elmentve')
		with open(filepath, 'a') as f:
			f.write(str(id)+"\n")
			email_sender = 'edkbrfid@freemail.hu'
			email_receiver = 'eredits.daniel@gmail.com'
			subject = 'RfidAdmin'
			msg = MIMEMultipart()
			msg['From'] = email_sender
			msg['To'] = email_receiver
			msg['Subject']= subject
			body = 'Egy uj rfid lett hozzaadva az adatbazishoz. Id: '+str(id)
			msg.attach(MIMEText(body, 'plain'))
			text = msg.as_string()
			connection = smtplib.SMTP('smtp.freemail.hu', 587)
			connection.starttls()
			connection.login(email_sender,'Mikroelektro2023')
			connection.sendmail(email_sender, email_receiver, text )
			connection.quit()
			print('Email elkuldve')
			song=AudioSegment.from_wav('/home/pi/edkb-rfid/reg_keszx.wav')
			play(song)
finally:
	GPIO.cleanup()

