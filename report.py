#!/usr/bin/env python3 

""" 
Report scripts is part of a thesis work about distributed systems 
"""
__author__ = "Bruno Chianca Ferreira"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Bruno Chianca Ferreira"
__email__ = "brunobcf@gmail.com"

# TODO #
# Remove / from the end of indir

libnames = ['pandas']
import sys
for libname in libnames:
    try:
        lib = __import__(libname)
    except:
        print (sys.exc_info())
    else:
        globals()[libname] = lib

import os, math, struct, sys, json, traceback, time, argparse, statistics, shutil, warnings
import uuid
import matplotlib.pyplot as plt
import numpy as np
pd = pandas
warnings.filterwarnings("ignore")
import numpy_indexed as npi

class Report ():

    def __init__ (self,folder, files):
        self.files = files
        self.folder = folder
        self.report_file = open(self.folder + "report" + ".txt","w")
        self.number_of_towers = 0
        self.number_of_aircrafts = 0
        #print(self.files)
        self.tower_files = {}
        self.aircraft_files = {}
        if arguments.plot:
            rep = self.pre_overall(arguments.plot)
            #self.folder = arguments.plot
            self.overall(rep)
            self.post_overall()
            sys.exit(1)
        self.open_files(files)
        self.latency()
        self.delivery()
        self.report_file.flush()
        self.report_file.close()
        self.archive_folder = str(time.localtime().tm_year) + "_" + str(time.localtime().tm_mon) + "_" + str(time.localtime().tm_mday) + "_" + str(time.localtime().tm_hour) + "_" + str(time.localtime().tm_min) + "-" + str(arguments.delay)
        try:
            os.mkdir(folder + self.archive_folder)
        except FileExistsError:
            print("Report folder already created.")
            pass
        for file in self.files: 
            shutil.copyfile(self.folder + file, self.folder + self.archive_folder + "/" + file)
        shutil.copyfile(self.folder + "report.txt", self.folder + self.archive_folder + "/" + "report.txt")
        #sys.exit(1)

    def pre_overall(self,folder):
        reps = []
        for (dirpath, dirnames, filenames) in os.walk(folder):
            reps.extend(dirnames)
            break
        reports = {}
        
        for rep in reps:
            reports[rep] = []
            for (dirpath, dirnames, filenames) in os.walk(folder + "/" + rep):
                reports[rep].extend(dirnames)
                break


        #style = dict(size=16, color='gray')
        self.fig, self.ax = plt.subplots(figsize=(6, 6), dpi=200)
        #self.ax.text(550, 65, "Simulation time horizon", **style)
        #self.ax.grid()
        return reports
        #print(reports.keys())
        #sys.exit(1)
    def post_overall(self):
        print(self.legendlabels)
        self.ax.legend(self.data,self.legendlabels,loc=1)
        plt.style.use('default')
        #plt.style.use(['science','ieee'])
        #plt.rcParams['text.usetex'] = True
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['font.size'] = 15
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plt.rcParams['xtick.major.size'] = 5.0
        plt.rcParams['xtick.minor.size'] = 3.0
        plt.rcParams['ytick.major.size'] = 5.0
        plt.rcParams['ytick.minor.size'] = 3.0
        plt.ylabel("Latency (ms)", fontsize=22)
        plt.xlabel("Broadcast delay (s)", fontsize=22)
        plt.yticks(fontsize=17)
        plt.xticks(fontsize=17)
        plt.grid(color = '#CCCCCC', linestyle = '--', linewidth = 0.5, which='major')
        plt.tight_layout()
        #print()
        name = ""
        for arg in arguments.plot.split("/"):
            if arg != "." and arg != ".." and arg != "":
                name = name + "_" + str(arg)
                
        #print(name + ".png")
        #sys.exit(1)
        plt.savefig(name + ".png")
        plt.close()
        #plt.show()

    def overall(self, _reports):
        markers = ["o","x","^","<",">","1","2","3","4",".",",","v"]
        mark = 0
        self.data = []
        self.legendlabels = []
        for rep, folders in _reports.items():
            #folders = []
            reports = {}
            delays = []
            latency = []
            stdev = []
            
            #print(arguments.plot+ str(rep))
            #self.overall(self.folder + rep)
        #for (dirpath, dirnames, filenames) in os.walk(folder):
        #    folders.extend(dirnames)
        #    break
        #print(folders)
            for report in folders:
                delay = float(report.split("-")[1])
                #print(delay)
                #print(float(report.split("-")[1]))
                if delay not in reports:
                    reports[delay] = []
                    reports[delay].append(report)
                else:
                    reports[delay].append(report)
        #print(reports)
            self.legendlabels.append(rep)
            for delay, reports in sorted(reports.items()):
                #print(delay)
                if delay not in delays:
                    delays.append(delay)
                #print(delay)
                #print(reports)
                _latency = []
                for report in reports:
                    #print(self.folder + rep + "/"+ report + "/report.txt")
                    #sys.exit(1)
                    self.report_file = open(arguments.plot + rep + "/"+ report + "/report.txt","r")
                    info = self.report_file.readlines()
                    for line in info:
                        if line.split(":")[0] == "Median latency":
                            l = float(line.split(":")[1].split(" ")[0])
                            #print(l)
                            _latency.append(l)
                    #sys.exit(1)
                latency.append(statistics.mean(_latency))
                stdev.append(statistics.stdev(_latency))
            #print(latency)
            #print(stdev)
            self.data.append(self.ax.scatter(delays,latency,s=70,color='k',marker=markers[mark]))
            mark += 1
            #data1   = self.ax.scatter(delays,latency,s=70,color='k',marker='^')
            self.ax.errorbar(delays, latency, yerr=stdev)
            self.ax.set_ylim([0, 300])


    def latency(self):
        latency = []
        for key,value in self.tower_files.items():
            for line in value:
                line = line.split(";")
                latency.append((int(line[0]) - int(line[1])) / 1000)
                #print(str(latency / 1000) + "ms")
        #print("Mean latency:\t" + str(statistics.mean(latency)) + " ms")
        self.report_file.write("Mean latency:\t" + str(statistics.mean(latency)) + " ms" + '\n')
        self.report_file.write("Median latency:\t" + str(statistics.median(latency)) + " ms"+ '\n')
        self.report_file.write("Latency std dev:" + str(statistics.stdev(latency)) + " ms" + '\n')
        #print("Median latency:\t" + str(statistics.median(latency)) + " ms")
        #print("Latency std dev:" + str(statistics.stdev(latency)) + " ms")

    def delivery(self):
        messages = {}
        delivered  = {}
        sent = {}
        for key,value in self.aircraft_files.items():
            sent[key] = len(value)
            delivered[key] = 0
            #print("Aircraft: " + str(key) + " sent " + str(sent[key]) + " messages")
            self.report_file.write("Aircraft: " + str(key) + " sent " + str(sent[key]) + " messages"+ '\n')
            for line in value:
                line = line.split(";")
                message_id = line[2]
                messages[message_id] = []
                for _key,_value in self.tower_files.items():
                    for _line in _value:
                        _line = _line.split(";")
                        _message_id = _line[2]
                        if _message_id == message_id:
                            if len(messages[message_id]) == 0:
                                #print(messages[message_id])
                                delivered[key] +=1
                            messages[message_id].append(_key)
                            break
            #print("Aircraft: " + str(key) + " delivered " + str(delivered[key]) + " messages")
            #print("Delivery rate: " + str( (delivered[key] / sent[key]) * 100 ) + " %")
            self.report_file.write("Aircraft: " + str(key) + " delivered " + str(delivered[key]) + " messages"+ '\n')
            self.report_file.write("Delivery rate: " + str( (delivered[key] / sent[key]) * 100 ) + " %" + '\n')
        
        #print(messages)
        reach = {}
        for i in range(0,self.number_of_towers+1):
            reach[i] = 0
        for message, delivery in messages.items():
            reach[len(delivery)] +=1

        self.report_file.write(str(reach)+ '\n')
        #print(reach)

    def open_files(self, files):
        print(files)
        for file in files:
            if file[:5] == "tower":
                tf = open(self.folder + file).readlines()
                tf.pop(0)
                self.tower_files[file.split(".")[0]] = tf
                #towers.append(self.folder + file)
            elif file[:3] == "uas":
                tf = open(self.folder + file).readlines()
                tf.pop(0)
                self.aircraft_files[file.split(".")[0]] = tf
        #print(aircraft_files.keys())
        self.number_of_towers = len(self.tower_files.keys())
        self.number_of_aircrafts = len(self.aircraft_files.keys())
        self.report_file.write("Number of towers: " + str(self.number_of_towers)+ '\n')
        self.report_file.write("Number of aircrafts: " + str(self.number_of_aircrafts)+ '\n')
        print("Number of towers: " + str(self.number_of_towers))
        print("Number of aircrafts: " + str(self.number_of_aircrafts))



if __name__ == '__main__':  #for main run the main function. This is only run when this main python file is called, not when imported as a class
    print("Reporter - Report generator for UTM")
    print()
    files = []
    folder = "./reports/"
    parser = argparse.ArgumentParser(description='Options as below')
    parser.add_argument("-d", "--delay", help="Delay between messages", type=float)
    parser.add_argument("-p", "--plot", help="Delay between messages", type=str)
    arguments = parser.parse_args()

    for (dirpath, dirnames, filenames) in os.walk(folder):
        files.extend(filenames)
        break

    report = Report(folder, files)
                
    sys.exit()
