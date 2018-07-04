# Dependencies
# pip install forex-python

# Run
# python foreign_exchange_reminder.py &

# Kill
# kill -9 {PID}

import smtplib
import sys
import time
import os
from time import gmtime
from email.mime.text import MIMEText
from forex_python.converter import CurrencyRates

class Reminder(object):

	def get_time(self):
		return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

	def write_log(self, log):
		with open("log.txt", "a") as logFile:
			logFile.write(self.get_time() + ">>> " + log + "\n")

	def send_email(self, message, target):
		text = "Hi " + target.split('@')[0] + ",\n\n"
		text += message
		msg = MIMEText(text, 'plain')
		me = os.environ['CURRENCY_EMAIL']
		password = os.environ['CURRENCY_PASSWORD']
		msg['Subject'] = 'Foreign Exchange Remind: ' + self.get_time()
		msg['From'] = me
		msg['To'] = target

		s = smtplib.SMTP('smtp.gmail.com:587')
		s.ehlo()
		s.starttls()
		s.login(me, password)
		s.sendmail(me, [target], msg.as_string())
		s.quit()

	def run(self):
		# record process id
		with open("process.txt", "a") as processFile:
			processFile.write(self.get_time() + " ---> PID: " + str(os.getpid()) + "\n")

		# add receivers
		targets = []
		targets.append("lucasliu12138@gmail.com")

		while True:
			# compose message
			cur = CurrencyRates()
			log_usd = cur.get_rate('USD', 'CNY')
			log_aud = cur.get_rate('AUD', 'CNY')
			log_jpy = cur.get_rate('JPY', 'CNY')
			self.write_log(str(cur.get_rates('CNY')))
			message = "1 USD = " + str(log_usd) + " CNY\n"
			message += "1 AUD = " + str(log_aud) + " CNY\n"
			message += "1 JPY = " + str(log_jpy) + " CNY\n"

			for target in targets:
				self.send_email(message, target)
			time.sleep(10)

if __name__ == "__main__":
	reminder = Reminder()
	reminder.run()