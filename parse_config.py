
import psjson
import traceback
from crontab import CronTab
import sys



#Parse:
    #extracts the individual dictionaries 
    #returns them:
        #has the option of returning any specific dictionary or all at once
    #creates and returns single task formatted for pScheduler given task info
    #creates and returns single task formatted for pSSID given task info
        #(with cron scheduler and SSID list)
    #creates and returns list of all tasks from config file formatted for pSSID
    #takes one argument: json configuration file

class Parse:

    def __init__(self, config_file):
        #psjson makes sure that it is a valid json file
        json_obj =  psjson.json_load(source=config_file)

        try:
            self.meta = json_obj["_meta"]
            self.archives = json_obj["archives"]
            self.tests = json_obj["tests"]
            self.tasks = json_obj["tasks"]
            self.schedules = json_obj["schedules"]
            self.SSID_list = json_obj["SSID_list"]
        except:
            print("ERROR: Make sure all fields are present")
            print(traceback.print_exc())



    #retuens the dicts in that order, to access individual see example tests below
    def return_all(self):
        return self.meta, self.archives, self.SSID_list, \
        self.tests, self.schedules, self.tasks



    #returns cron schedule list for a given task
    def schedule_for_task(self,given_task):
        try:
            cron_list = []
            schedlist = self.tasks[given_task]["schedule"]
            for i in schedlist:
                tasksched = self.schedules[i]
                cron_list.append(CronTab(str(tasksched["repeat"])))
        except:
            print("ERROR in retrieving \"schedule\" from", given_task)
            print(traceback.print_exc())

        return cron_list




    def SSIDs_for_task(self,given_task):        
        try:
            ssids = []            
            ssidlist = self.tasks[given_task]["SSIDs"]
            for i in ssidlist:
                ssid = self.SSID_list[i]
                ssids.append(ssid)
        except:
            print("ERROR in retrieving \"SSIDs\" from", given_task)
            print(traceback.print_exc())

        return ssids



    
    #option to get a pscheduler formatted for specific task
    #running this function validates every key(archives,tests, etc) also valid
    def create_pScheduler_task(self, given_task):
        #scheudler needs to be empty when sent to pScheduler
        taskobj = {
            "schema" : 1,
            "schedule": {}
        }
        #validate tests
        try:
            taskobj["test"]= self.tests[self.tasks[given_task]["test"]]
        except:
            print("ERROR in retrieving \"test\" from", given_task)
            print(traceback.print_exc())        
        #validate archives
        try:
            taskobj["archives"] = []
            archives_list = self.tasks[given_task]["archives"]
            for i in archives_list:
                taskobj["archives"].append(self.archives[i])
        except:
            print("ERROR in retrieving \"archives\" from", given_task)
            print(traceback.print_exc())
        return taskobj


    
    # running this function validates SSIDs and schedule
    # pSSID task object. Dict keys: TASK, Sched, SSIDS
    # TASKS: contain formatted tasks for valid for pscheduler
    # Sched: list of cron schedule info
    # SSIDs: list of SSIDs associated with task
    def create_pSSID_task(self, given_task):
        taskobj = {}
        taskobj["Name"] = given_task
        taskobj["TASK"] = self.create_pScheduler_task(given_task)

        #Attaching schedule
        taskobj["Sched"] = self.schedule_for_task(given_task)

        #Attaching SSIDs 
        taskobj["SSIDs"] = self.SSIDs_for_task(given_task)

        return taskobj

    

    #option to return list of pSSID task objects. Dict keys: TASK, Sched, SSIDS
    def pSSID_task_list(self):
        TASKS = []
        for eachtask in self.tasks:
            TASKS.append(self.create_pSSID_task(eachtask))

        return TASKS




#sub-main for testing purposes
#also serves as usage

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print ("ERROR: Provide JSON file")
        print ("USAGE: python %s filename.json" % sys.argv[0])
        exit(1)
    elif len(sys.argv) > 2: 
        print ("ERROR: Only Provide JSON file")
        print ("USAGE: python %s filename.json" % sys.argv[0])
        exit(1)

    config_file = open(sys.argv[1], "r")

    p = Parse(config_file)

    #single dict test:
    #optionally use psjson.json_dump() to pretty print
    print("SINGLE")
    print("meta:", p.meta)
    print("archives:", p.archives)
    print("SSID_list:", p.SSID_list)
    print("tests:", p.tests)
    print("schedules:", p.schedules)
    print("tasks:", p.tasks)
    print("SINGLE END")
    print
    print
    print

    #pscheduler task
    psched = p.create_pScheduler_task("example_task_rtt")
    print(psched)
    print
    print
    print



    #pSSID task
    pssid = p.create_pSSID_task("example_task_rtt")
    print(pssid)
    print
    print
    print

    #task list
    print(p.pSSID_task_list())
    print
    print
    print


    #TODO XXX: more tests


    exit(0)

#DEBUG:
    
        # try:
        #     #Attaching schedule
        #     taskobj["Sched"] = []
        #     schedlist = self.tasks[given_task]["schedule"]

        #     for i in schedlist:
        #         tasksched = self.schedules[i]
        #         taskobj["Sched"].append(CronTab(str(tasksched["repeat"])))
        # except:
        #     print("ERROR in retrieving \"schedule\" from", given_task)
        #     print(traceback.print_exc())

        # try:
        #     #Attaching SSIDs 
        #     taskobj["SSIDs"] = []
        #     ssidlist = self.tasks[given_task]["SSIDs"]

        #     for i in ssidlist:
        #         ssid = self.SSID_list[i]
        #         taskobj["SSIDs"].append(ssid)
        # except:
        #     print("ERROR in retrieving \"SSIDs\" from", given_task)
        #     print(traceback.print_exc())
