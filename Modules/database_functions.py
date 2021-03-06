import mysql.connector
import sys
from datetime import date
from datetime import datetime

from config import *




mydb=mysql.connector.connect(host=dbhost, user=dbuser, password=dbpassword, database=dbname, auth_plugin='mysql_native_password')
mycursor = mydb.cursor()


class Account:
    ID = 0
    Enabled = 0
    name = ""
    user = ""
    fingerprint = ""
    tenancy = ""
    homeregion = ""
    key = ""
    CreatedByKey = ""

def GetAccounts():
    a = []
    myquery = "select * from Accounts"
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(myquery)
    myresult = mycursor.fetchall()
    for r in myresult:
        account = Account()
        account.ID = r["ID"]
        account.Enabled = r["Enabled"]
        account.name = r["name"]
        account.user = r["user"]
        account.tenancy = r["tenancy"]
        account.fingerprint = r["fingerprint"]
        account.homeregion = r["homeregion"]
        account.key = r["key"]
        account.CreatedByKey = r["CreatedByKey"]
        a.append(account)

    return a


class InventoryObject:

    def __init__(self):
        self.cloud = ""
        self.Account = ""
        self.Region = ""
        self.Owner = ""
        self.InventoryDate = ""
        self.CreatedDate = ""
        self.Service = ""
        self.ServiceID = ""
        self.Name = ""
        self.State = ""
        self.ServiceDetail = ""
        self.Location = ""
        self.LocationOwner = ""
        self.MasterResource = ""
        self.CPU = 0
        self.GPU = 0
        self.Memory = 0
        self.LocalStorage = 0
        self.AttachedStorage = 0

    def SaveItem(self):
        print ("Saving item {}".format(self.Name))
        fields = ""
        fieldvalues = ""

        for item in self.__dict__:
            fields = fields + item + ","
            if type(self.__dict__[item]) is str:
                v = self.__dict__[item]
                fieldvalues = fieldvalues + "'{}',".format(v)
            if type(self.__dict__[item]) is int:
                fieldvalues = fieldvalues + "{},".format(self.__dict__[item])
            if type(self.__dict__[item]) is datetime:
                v = self.__dict__[item]
                fieldvalues = fieldvalues + "'{}',".format(v)

        fields = fields.rstrip(",")
        fieldvalues = fieldvalues.rstrip(",")
        myquery = "insert into resources ({}) values ({})".format(fields, fieldvalues)

        mycursor.execute(myquery)
        mydb.commit()





