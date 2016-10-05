#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

website: orchidinfosys.com 
last edited: October 2015
"""
from time import strftime
from sys import argv
import xmlrpclib
import os
from datetime import datetime , timedelta
from zklib import zklib
import time
from zklib import zkconst
import re

print "argv>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",argv
#DBNAME ='yas_test'
#USERNSME = 'admin' 
#PASSW = 'fslhggihgvplkhgvpdl'     
#IP_URL ='128.199.148.185:9069'

DBNAME ='anaf_local'
USERNSME = 'admin' 
PASSW = 'admin'     
IP_URL ='localhost:8069'

class orchid_service:
    def getsock(self):
        url ='http://'+IP_URL
        sock_common = xmlrpclib.ServerProxy (url+'/xmlrpc/common')
        uid = sock_common.login(DBNAME, USERNSME, PASSW) 
        sock = xmlrpclib.ServerProxy(url+'/xmlrpc/object')
        return uid,sock
        

    def get_outlets(self):
        args = [] #query clause
        uid,sock = self.getsock()
        ids = sock.execute(DBNAME, uid, PASSW, 'pos.config', 'search', args)
        fields = ['name','name'] #fields to read
        data = sock.execute(DBNAME, uid, PASSW, 'pos.config', 'read', ids, fields) 
        return data
    
    def download_attendance(self):
        
        uid,sock = self.getsock()
        
        machine_ip = argv[1]
        port = argv[2]
        zk = zklib.ZKLib(machine_ip, int(port))
        res = zk.connect()
        
        if res == True:
            zk.enableDevice()
            zk.disableDevice()
            attendance = zk.getAttendance()
           
            if (attendance):
                for lattendance in attendance:
                    if lattendance[1] == 1:
                        state = 'check_out'
                    elif lattendance[1] == 0:
                        state = 'check_in'
                    
                    time_att = str(lattendance[2].date()) + ' ' +str(lattendance[2].time())
                    atten_time1 = datetime.strptime(str(time_att), '%Y-%m-%d %H:%M:%S')
                    atten_time = atten_time1 - timedelta(hours=4)
                    atten_time = datetime.strftime(atten_time,'%Y-%m-%d %H:%M:%S')
                   
                    print time_att,lattendance[0]
                    try:
                        args = [('emp_code','=',str(lattendance[0])),('name','=',atten_time)]
                        del_atten_ids = sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'search', args)
                        
                        if del_atten_ids:
                            continue
                        else:
                            
                            
                            cleanString = machine_ip.replace('\n',' ')
                            dom = [('name','=',cleanString)]
                            machine_id = sock.execute(DBNAME, uid, PASSW, 'biometric.machine', 'search', dom)
                            if machine_id:
                                attend_data= {'name':atten_time,'emp_code':lattendance[0],'mechine_id':machine_id[0],'state':state}
                                sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'create', attend_data)
                            else:
                                machine_id =sock.execute(DBNAME, uid, PASSW, 'biometric.machine', 'create', {'name':machine_ip})
                                attend_data= {'name':atten_time,'emp_code':lattendance[0],'mechine_id':machine_id,'state':state}
                                sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'create', attend_data)
                               
                          
                    except Exception,e:
                        pass
                        print "exception..Attendance creation======",e, e.args
#            zk.enableDevice()
#            zk.disconnect()
            return True
        else:
            print "Exception>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        


odoo = orchid_service()
odoo.download_attendance()




