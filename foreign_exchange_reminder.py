# Dependencies
# forex-python
# matplotlib

# Run
# python foreign_exchange_reminder.py &

# Kill
# kill -9 {PID}

import smtplib
import sys
import datetime
import time
import os
import subprocess
import matplotlib.pyplot as plt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from forex_python.converter import CurrencyRates

class Reminder(object):

	def get_time(self):
		return datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')

	def write_log(self, log):
		with open('log.txt', 'a') as logFile:
			logFile.write(self.get_time() + '>>> ' + log + '\n')

	def get_last_month_data(self):
		cur = CurrencyRates()
		x = []
		y_usd = []
		y_aud = []
		y_jpy = []
		last_week_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(-29)
		count_date = 0
		while count_date < 30:
			x.append(last_week_date.strftime('%Y-%m-%d'))
			y_usd.append(cur.get_rate('USD', 'CNY', last_week_date))
			y_aud.append(cur.get_rate('AUD', 'CNY', last_week_date))
			y_jpy.append(cur.get_rate('JPY', 'CNY', last_week_date))
			last_week_date += datetime.timedelta(1)
			count_date += 1
		return (x, y_usd, y_aud, y_jpy)

	def visualize(self, x, y, currency, background_color, line_color, min_y, max_y):

		# set y boundary to make it look better
		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.set_ylim(ymin=min_y, ymax=max_y)

		plt.fill_between( x, y, color=background_color, alpha=0.5)
		plt.plot(x, y, color=line_color, alpha=0.7)
		plt.xlabel('Date')
		plt.ylabel('Equivalent CNY')
		plt.title(currency + ' to CNY Weekly Report')
		# fix x axis labels overlap
		ax.xaxis.set_major_locator(plt.NullLocator())

		# TODO: improve the x axis (https://jakevdp.github.io/PythonDataScienceHandbook/04.10-customizing-ticks.html)
		# ax.xaxis.set_major_locator(plt.MaxNLocator(10))
		# fig.autofmt_xdate()

		plt.savefig(currency + '.png')
		# clear figure to avoid overlap
		plt.clf()

	def read_registers(self):
		with open('register.txt') as registerFile:
			rows = registerFile.readlines()
		return [row.strip() for row in rows]


	def send_email(self, html, target):
		part_main = MIMEText(html, 'html')
		msg = MIMEMultipart('alternative')
		msg.attach(part_main)

		# attach images
		part_usd = MIMEBase('application', "report")
		part_usd.set_payload(open('USD.png', "rb").read())
		encode_base64(part_usd)
		img_usd = os.path.basename('USD.png')
		part_usd.add_header('Content-Disposition', 'attachment; filename= "%s"' % img_usd)
		# Content-ID is for embedding image into html, otherwise it will remain in attachment
		part_usd.add_header('Content-ID', '<image_usd>')
		msg.attach(part_usd)

		part_aud = MIMEBase('application', "report")
		part_aud.set_payload(open('AUD.png', "rb").read())
		encode_base64(part_aud)
		img_aud = os.path.basename('AUD.png')
		part_aud.add_header('Content-Disposition', 'attachment; filename= "%s"' % img_aud)
		part_aud.add_header('Content-ID', '<image_aud>')
		msg.attach(part_aud)

		part_jpy = MIMEBase('application', "report")
		part_jpy.set_payload(open('JPY.png', "rb").read())
		encode_base64(part_jpy)
		img_jpy = os.path.basename('JPY.png')
		part_jpy.add_header('Content-Disposition', 'attachment; filename= "%s"' % img_jpy)
		part_jpy.add_header('Content-ID', '<image_jpy>')
		msg.attach(part_jpy)

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
		with open('process.txt', 'a') as processFile:
			processFile.write(self.get_time() + ' ---> PID: ' + str(os.getpid()) + '\n')

		while True:
			# compose message
			cur = CurrencyRates()
			now_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
			log_usd = str(cur.get_rate('USD', 'CNY', now_time))
			log_aud = str(cur.get_rate('AUD', 'CNY', now_time))
			log_jpy = str(cur.get_rate('JPY', 'CNY', now_time))
			data_list = [log_usd, log_aud, log_jpy]
			self.write_log(str(cur.get_rates('CNY', now_time)))
			last_week_data = self.get_last_month_data()
			self.visualize(last_week_data[0], last_week_data[1], 'USD','skyblue', 'slateblue', min(last_week_data[1]) - 0.1, max(last_week_data[1]) + 0.1)
			self.visualize(last_week_data[0], last_week_data[2], 'AUD','darkgreen', 'limegreen', min(last_week_data[2]) - 0.1, max(last_week_data[2]) + 0.1)
			self.visualize(last_week_data[0], last_week_data[3], 'JPY','orangered', 'salmon', min(last_week_data[3]) - 0.01, max(last_week_data[3]) + 0.01)

			message_usd = '1 USD = ' + log_usd + ' CNY\n'
			message_aud = '1 AUD = ' + log_aud + ' CNY\n'
			message_jpy = '1 JPY = ' + log_jpy + ' CNY\n'

			html = """\
			<html>
				<head></head>
				<body>
				<p>Hi!
					<br>How are you? I would like to show you our daily foreign exchange report!
					<br>%s
					<br><img src="cid:image_usd">
					<br>%s
					<br><img src="cid:image_aud">
					<br>%s
					<br><img src="cid:image_jpy">
					<br>Report figures have been attached to this email!
					<br>Here is my <a href="http://www.lucas-liu.com">blog</a>, if you want to know more about me.
					<br>Thanks for your registration!
				</p>
				</body>
			</html>
			""" % (message_usd, message_aud, message_jpy)

			registers = self.read_registers()
			for register in registers:
				self.send_email(html, register)
			# daily
			time.sleep(24 * 60 * 60)

if __name__ == '__main__':
	reminder = Reminder()
	reminder.run()