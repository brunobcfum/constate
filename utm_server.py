#!/usr/bin/env python3

""" 
Network class is part of a thesis work about distributed systems 
"""
__author__ = "Bruno Chianca Ferreira"
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Bruno Chianca Ferreira"
__email__ = "brunobcf@gmail.com"

# Python stdlib
from os import execl
import sys
import pickle
import json
import time
import argparse
import threading
import logging
from collections import deque
#etcd
import etcd3
#local
import network_sockets

class UTMServer():
  """
  Emulates a simple implementation of the UAS endpoint on a UTM data service provider

  .. note::

      Each instance will be a separate thread with a open socket, thread runs in infinit loop and self.running must be set to False to end the thread.

  """
  def __init__(self, tag, timer):
    """UTMServer UAS endpoint

    Args:
        tag (str) - A unique identifier for the UTM server
        timer (int) - For how long the session should run in seconds

    Kwargs:
        

    """
    self.tag = tag
    self.start = int(time.time())
    self.timer = timer
    self.cache = deque([], maxlen=1000)
    self._setup()
    while int(time.time()) < (self.start + self.timer):
      time.sleep(0.001)
    print("Session ended")
    self.save_to_file()

  def _setup(self):
    """ 
    Runs initial configuration

    Parameters
    ----------

    Returns
    --------

    """
    self.data_bank = []
    self.report_file = open("/home/bruno/Documents/bruno-onera-enac-doctorate/software/utm/reports/" + self.tag + ".csv","w")
    self.report_file.write('time;created;id;aircraft;position;vel;status\n')
    self.utm_interface = network_sockets.TcpPersistent(self.utm_packet_handler, debug=False, port=55555, interface='')
    self.uas_interface = network_sockets.UdpInterface(self.uas_packet_handler, debug=False, port=44444, interface='')
    self.utm_interface.start()
    self.uas_interface.start()
    try:
      self.etcd = etcd3.client()
      self.etcd.add_watch_callback('uas', self.etcd_callback, range_end='uas999')
    except:
      logging.info("Running UTM server without etcd")

  def etcd_callback(self, _event):
    """ 
    Callback function called everytime etcd senses data change in configure key

    Parameters
    ----------
    _event (list) - ETCD event list

    Returns
    --------

    """
    try:
      for event in _event.events:
        aircraft_data, _ = self.etcd.get(event.key)
        aircraft_data.decode()

        data = json.loads(aircraft_data)

        unique_id = data['msg-id']
        aircraft_id = event.key.decode()
        position = data['position']
        velocity = data['velocity']
        status = data['status']
        created = data['created']

        data = str(int(time.time()*1000000)) + ";" + str(created) + ";" + str(unique_id) + ";" + str(aircraft_id) + ";" + str(position)+ ";" + str(velocity)+ ";" + str(status)

        self.save_historic(data)
    except:
      logging.error("UTMServer>etcd_callback>Error getting data from ETCD")

  def save_historic(self, data):
    """ 
    Save updated aircraft data in historic database

    Parameters
    ----------
    data (list) - aircraft data
      current_time - Current time when saving
      created_time - Time data was created
      unique_id - Unique message id on creation
      aircraft_id - Aircraft id
      position - Current aircraft position
      velocity - Current aircraft velocity
      status - Current aircraft status

    Returns
    --------

    """    
    self.data_bank.append(data)


  def callback_thread(self, event):
    """ 
    Deprecated

    """    
    try:
      aircraft_data, _ = self.etcd.get(event.key)
    except:
      pass
    aircraft_data.decode()
    data = json.loads(aircraft_data)
    unique_id = data['msg-id']
    aircraft_id = event.key.decode()
    position = data['position']
    velocity = data['velocity']
    status = data['status']
    created = data['created']
    data = str(int(time.time()*1000000)) + ";" + str(created) + ";" + str(unique_id) + ";" + str(aircraft_id) + ";" + str(position)+ ";" + str(velocity)+ ";" + str(status)
    self.data_bank.append(data)


  def save_to_file(self):
    """ 
    Save databank to file

    Parameters
    ----------

    Returns
    --------
    
    """
    try: 
      for data in self.data_bank:
        self.report_file.write(data + '\n')
    except:
      logging.error("UTMServer>save_to_file>Error saving databack to file")

    self.report_file.flush()
    self.report_file.close()
        

  def utm_packet_handler(self, payload, sender_ip, connection):
    """ 
    UTM packet handler
    Called when data arrives on UTM endpoint

    Parameters
    ----------
    payload (bin) - Pickled payload
    sender_ip (str) - Sender's IP address 
    connection (socket) - Connection open socket

    Returns
    --------

    """
    pass

  def uas_packet_handler(self, payload, sender_ip, connection):
    """ 
    UAS packet handler
    Called when data arrives on UAS endpoint

    Parameters
    ----------
    payload (bin) - Pickled payload
    sender_ip (str) - Sender's IP address 
    connection (socket) - Connection open socket

    Returns
    --------

    """
    try:
      payload = pickle.loads(payload)
    except:
      logging.error("UTMServer>utm_packet_handler>Received invalid UDP packet")

    unique_id = payload[0]

    created = payload[1][0]
    aircraft_id = payload[1][1]
    position = payload[1][2]
    velocity = payload[1][3]
    status = payload[1][4]

    data = json.dumps({"created" : created,
                       "msg-id" : unique_id,
                       "position" : position,
                       "velocity" : velocity,
                       "status" : status,
    })

    self.write_to_etcd(aircraft_id, data)

  def write_to_etcd(self, aircraft_id, data):
    """ 
    Write data to ETCD

    Parameters
    ----------
    aircraft_id (str) - unique aircraft ID
    data (list) - data

    Returns
    --------
    
    """
    try:
      self.etcd.put(aircraft_id, data)
    except:
      pass

#######################Class END###############################################################################################

def parse_args():
  """ 
  Method for parsing command line arguments

  Parameters
  ----------

  Returns
  --------
  args - Arguments

  """
  parser = argparse.ArgumentParser(description='Some arguments are obligatory and must follow the correct order as indicated')
  parser.add_argument("-t", "--tag", help="Tag name", type=str)
  return parser.parse_args()

def set_logging():
  """ 
  Sets the logging levels

  Parameters
  ----------

  Returns
  --------

  """
  logging.Formatter('%(asctime)s -> [%(levelname)s] %(message)s')
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)
  logging.basicConfig(level='INFO')

###########################Runner ################################################################################################


if __name__ == '__main__':
  set_logging()
  logging.info("Starting UTM server")
  args = parse_args()
  try:
    UTMServer(args.tag, 120)
  except KeyboardInterrupt:
    logging.info("Exiting UTM Server")



