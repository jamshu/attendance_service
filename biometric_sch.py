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
import time
from config import config


print "config>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",config


#DBNAME ='yas_test'
#USERNSME = 'admin' 
#PASSW = 'fslhggihgvplkhgvpdl'     
#IP_URL ='128.199.148.185:9069'


DBNAME ='yas_live'
USERNSME = 'admin' 
PASSW = 'fslhggihgvplkhgvpdl'     
IP_URL ='128.199.148.185'




#DBNAME ='yas_live'
#USERNSME = 'admin' 
#PASSW = 'fslhggihgvplkhgvpdl'     
#IP_URL ='128.199.148.185'

#DBNAME ='anaf_local'
#USERNSME = 'admin' 
#PASSW = 'admin'     
#IP_URL ='localhost:8069'

#DBNAME ='yas_live'
#USERNSME = 'admin' 
#PASSW = '123'     
#IP_URL ='localhost:8069'

class orchid_service:
    def getsock(self):
        url ='http://'+IP_URL
        sock_common = xmlrpclib.ServerProxy (url+'/xmlrpc/common')
        uid = sock_common.login(DBNAME, USERNSME, PASSW) 
        sock = xmlrpclib.ServerProxy(url+'/xmlrpc/object')
        return uid,sock
        
    def get_today(self):
        now = datetime.now()
        return str(now)[:10]
   
    
    def download_attendance(self):
        ''' Actulally uploading data to server by utlity from machine    '''
        
        uid,sock = self.getsock()
        
#        machine_ip = argv[1]
#        port = argv[2]
#        conf_file = open('machine_ip.txt', 'r')
#        
#        machine_vals = conf_file.readlines()
#        machine_ip = machine_vals[0].replace("\r\n","")
#        port = machine_vals[1].replace("\r\n","")
        
#        machine_ip = machine_ip.replace("\n","")
#        port = port.replace("\n","")
        
        machine_ip = config.get('ip')
        port = config.get('port',4370)
        outlet_id = config.get('outlet_id',False)
        company_id = config.get('company_id',False)

        zk = zklib.ZKLib(machine_ip, int(port))
        res = zk.connect()
        print "res>>>>>>>>>>>>>>>>>>>>>>>>>>",res
        if res == True:
            serial_no = ''
            s_no = zk.serialNumber()
            if s_no:
                s_no = s_no.replace('\n\t\r',"")
                serial = s_no[14:]
                serial_no = serial.split('\x00')[0]
        int_count = 0
        
        while res:
            int_count +=1
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
                    try:
                        args = [('emp_code','=',str(lattendance[0])),('name','=',atten_time)]
                        del_atten_ids = sock.execute(DBNAME, uid, PASSW, 'biometric.data.line', 'search', args)
                        
                        if del_atten_ids:
                            continue
                        else:
                            today = self.get_today()
                            dom = [('name','=',str(machine_ip))]
                            machine_id = sock.execute(DBNAME, uid, PASSW, 'biometric.machine', 'search', dom)
                            if machine_id:
                                dom1 = [('machine_id','=', machine_id[0]),('name','=',today),('outlet_id','=',outlet_id)]
                                bio_data_id = sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'search', dom1)
                                if bio_data_id:
                                    attend_data= {'name':atten_time,'emp_code':lattendance[0],'machine_id':machine_id[0],'state':state,'serial_no':serial_no,'bio_data_id':bio_data_id[0],'outlet_id':outlet_id}
                                    sock.execute(DBNAME, uid, PASSW, 'biometric.data.line', 'create', attend_data)
                                else:
                                    bio_data_id =sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'create', {'name':today,'machine_id':machine_id[0],'outlet_id':outlet_id,'company_id':company_id})
                                    attend_data= {'name':atten_time,'emp_code':lattendance[0],'machine_id':machine_id[0],'state':state,'serial_no':serial_no,'bio_data_id':bio_data_id,'outlet_id':outlet_id}
                                    sock.execute(DBNAME, uid, PASSW, 'biometric.data.line', 'create', attend_data)
                            else:
                                machine_id =sock.execute(DBNAME, uid, PASSW, 'biometric.machine', 'create', {'name':str(machine_ip),'serial_no':serial_no,'outlet_id':outlet_id,'company_id':company_id})
                                bio_data_id =sock.execute(DBNAME, uid, PASSW, 'biometric.data', 'create', {'name':today,'machine_id':machine_id,'outlet_id':outlet_id,'company_id':company_id})
                                attend_data= {'name':atten_time,'emp_code':lattendance[0],'machine_id':machine_id,'state':state,'serial_no':serial_no,'bio_data_id':bio_data_id,'outlet_id':outlet_id,'company_id':company_id}
                                sock.execute(DBNAME, uid, PASSW, 'biometric.data.line', 'create', attend_data)
                    except Exception,e:
                        print "exception..Attendance creation======"

            return True
        else:
            print "Exception>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        


odoo = orchid_service()
#odoo.download_attendance()

interval = config.get('interval_in_minute',5)
freq = interval * 60
count =0
while True:
    count +=1
    print "loop count >>>>>>>>>>>>>>",count
    odoo.download_attendance()
    time.sleep(freq)




