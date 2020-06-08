# queue strategy
# foreach task
#  schedule it at the appropriate time
#  use schedule.py
#  schedule.py sub-main will take a config and by default print the next occurance
# of each task.  Should also include an optional time duration, if so, print the schedule
# for the given duration


#myapi is Mark's modified REST script
import myapi

import datetime
import dateutil.parser
import json
from io import StringIO
import time
import traceback
import daemon

from dateutil.tz import tzlocal, tzwinlocal
import sys
import sched
from parse_config import Parse
import syslog

count = 0


# def custom_time():
# 	temp_time = 0
# 	temp_time = time.gmtime(time.time())



# 	return time.mktime(temp_time)



def run_schedule(eachtask, name, eachssid):
	global count
	count += 1
	print
	print("Main reached", count)
	print ("NOW: %s" % time.ctime(time.time()))
	print ("TASK: ", str(name))
	print ("SSID: ", str(eachssid["name"]))
	print ("Result URL: ")

	#reschedule should be sent an offset time
	#s.reschedule(eachtask, name, eachssid)
	myapi.main(eachtask["TASK"])
	print




class Schedule:

	def __init__(self, config_file):
		self.p = Parse(config_file)
		self.s = sched.scheduler(time.time, time.sleep)


	

	#this function should be called right after testing loop is reached
    #reschedule needs an offset
    #reschedule takes care of specific specific ssid for a specific task
	def reschedule(self,given_task, name, given_ssid, given_time):
		set_time = time.time()
		if given_time > time.time():
			set_time = given_time
		

		cron_list = given_task["Sched"]
		for eachcron in cron_list:
			schedule_time =  set_time  + eachcron.next(set_time)

			# print
			# print name
			# print given_ssid["name"]
			# print eachcron.next(set_time)
			# print(time.ctime(time.time()))
			# print(time.ctime(int(time.time())-int(time.time())%60))
			# print(time.ctime(schedule_time))
			# print "*****"
			# print
			self.s.enterabs(schedule_time, 1, run_schedule, argument = (given_task,name,given_ssid,))


	

	#schedules for all tasks at the start
	#"main" needs to be replaced with loop that tests each SSID
	#returns schedule queue
	#if this is called again insted of rschedule, the task that have not run will be scheduled twice for the same time
	def initial_schedule(self, given_time):
		TASKS = self.p.pSSID_task_list()

		for eachtask in TASKS:
			cron_list = eachtask["Sched"]
			ssid_list = eachtask["SSIDs"]
			name = eachtask["Name"]

			for eachssid in ssid_list:				
				self.reschedule(eachtask, name, eachssid, given_time)
    	
	


	def print_queue(self, given_time=time.time()):
		#print self.s.queue

		print
		print
		print
		print ("Now: ", time.ctime(time.time()))
		print ("start: ", time.ctime(given_time))
		
		# task = []
		# ssid = []

		#the next scheduled run for unique task/ssid comb
		temp = {}
		for i in self.s.queue:
			if i.argument[1] not in temp:
				temp[i.argument[1]] = []
				temp[i.argument[1]].append(i.argument[2]["name"])
				print_syslog = "First: " + time.ctime(i.time) + \
					" SSID: " + i.argument[2]["name"] + \
					" Test: " + i.argument[1]

				print (print_syslog)

				syslog.openlog("SCHEDULE", 0, syslog.LOG_LOCAL3)
				syslog.syslog(syslog.LOG_DEBUG, print_syslog)
				syslog.closelog()
				# print "First: %s" % time.ctime(i.time),
				# print "SSID: %s" %i.argument[2]["name"], 
				# print "Test: %s" % i.argument[1]
			elif i.argument[2]["name"] not in temp[i.argument[1]]:
				temp[i.argument[1]].append(i.argument[2]["name"])
				print_syslog = "First: " + time.ctime(i.time) + \
					" SSID: " + i.argument[2]["name"] + \
					" Test: " + i.argument[1]
				syslog.openlog("SCHEDULE", 0, syslog.LOG_LOCAL3)
				syslog.syslog(syslog.LOG_DEBUG, print_syslog)
				syslog.closelog()

				print (print_syslog)

	

	def run(self):
		print("RUN")
		self.s.run()

		


def time_input_error():
	print ("please provide a valid time: \
			\"[yyyy-mm-dd-hh-min]\" ")



def main():

	start = time.time()


	if len(sys.argv) < 2:
		print ("ERROR: Provide JSON file and optional start time")
		print( "USAGE: python %s filename.json [yyyy-mm-dd-hh-min]" % sys.argv[0])
		exit(1)
	elif len(sys.argv) == 3: 
		#check for valid time range and parse it
		start_time = sys.argv[2]

		#TODO: check number of options provided
		#num_opts = time_range.count("-")

		try:
			#all strings	
			year = (start_time.split("-")[0]).lstrip().rstrip()
			month = (start_time.split("-")[1]).lstrip().rstrip()
			day = (start_time.split("-")[2]).lstrip().rstrip()
			hour = (start_time.split("-")[3]).lstrip().rstrip()
			minute = (start_time.split("-")[4]).lstrip().rstrip()
		except:
			time_input_error()
			print(traceback.print_exc())
			exit(1)
		
		
		#TODO: are they all digits?


		start_str = year+" "+month+" "+day+" "+hour+" "+minute

		try:
			start = time.strptime(start_str, "%Y %m %d %H %M")
			start = time.mktime(start)
			print("start", time.ctime(start))
		except:
			time_input_error()
			print(traceback.print_exc())
			exit(1)

		time_given = True




	config_file = open(sys.argv[1], "r")
	s = Schedule(config_file)
	s.initial_schedule(start)
	s.print_queue(start)
	s.run()

	exit(0)


if __name__ == '__main__':
	with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, working_directory='/home/vagrant'):
		main()
