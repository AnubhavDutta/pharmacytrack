from flask import Flask, render_template, redirect, flash, url_for, request
from pymongo import MongoClient
import math

client=MongoClient('mongodb://localhost:27017')
db=client['pharmacy']
global hospitals
hospitals=db.shops
global allhopitals

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
    info=""
    allhopitals=hospitals.find()
    if request.method=="POST":
        try:
            hosid=int(request.form['hospnumber'])
            state=int(request.form['status'])
            pw=str(request.form['pw'])
            
            updations={
                "status":state,
            }
            allhopitals=hospitals.find({'number':hosid}).limit(1)
            if(allhopitals[0]['key']!=pw):
                allhopitals=hospitals.find()
                return render_template("dashboard.html",info=allhopitals)
            newvalues = { "$set": updations}
            hospitals.update_one({'number':hosid}, newvalues)
            allhopitals=hospitals.find()
            return render_template("dashboard.html",info=allhopitals)
        except:
            allhopitals=hospitals.find()
            return render_template("dashboard.html",info=allhopitals)
    return render_template("dashboard.html",info=allhopitals)


@app.route('/new/',methods=['GET','POST'])
def newHospital():
    return render_template("facility.html")

def distance(lat1, lat2,long1,long2):
    ang1=abs(lat1-lat2)
    ang2=abs(long1-long2)
    return math.sqrt((ang1**2)+(ang2**2))
    print("WITHIN DISTANCE FUNCTION")
def showdist(x):
    print("DOORI = ",x['distance'])
    return x['distance']
@app.route('/nearby/',methods=['GET','POST'])
def nearby():
    print("testinghello")
    if request.method=="POST":
        lat=float(request.form['lat'])
        lat=round(lat,7)
        long=float(request.form['long'])
        long=round(long,7)
        myhopitals=hospitals.find()
        used={}
        print("testing")
        maxind=-1
        allhopitals=[]
        for i in myhopitals:
            i['distance']=distance(lat, i['lat'] , long , i['long'])
            allhopitals=allhopitals+[i]
            maxind+=1
            used[maxind]=False

        #print("Wallhopitals is ",allhopitals)
        #allhopitals=allhopitals.sort(key=showdist)
        print("vvv",maxind)
        result=[]
        for g in range(5):
            index=0
            minPoint=float('inf')
            minInd=0
            minItem=None
            vvv=0+maxind

            #for ik in range(maxind+1)
            ik=0
            while ik<=maxind:
                i=allhopitals[ik]
                if( i['distance'] < minPoint):
                    minPoint=i['distance']
                    minItem=i
                    minInd=index
                index+=1
                ik+=1

            result=result+[minItem]
            del allhopitals[minInd]
            maxind-=1
            used[minInd]=True
            vvv=vvv-1
            if(vvv<0):
                break
        finalresult=[]
        for i in result:
            if(i['status']!=0):
                finalresult=finalresult+[i]
        return render_template("dashboard.html",info=finalresult, near=True)
    else:
        allhopitals=hospitals.find()
        return render_template("dashboard.html",info=allhopitals)

@app.route('/processing/',methods=['GET','POST'])
def process():
    if request.method=="POST":
        case=0
        try:
            hospname=str(request.form['addfac'])
            city=str(request.form['addcity'])
            if ("'" in hospname or '"' in hospname):
                throw
            if ("'" in city or '"' in city):
                throw
            case=1
            lat=float(request.form['lat'])
            lat=round(lat,4)
            long=float(request.form['long'])
            long=round(long,4)
            case=2
            pw=str(request.form['mykey'])
            
            allhopitals=hospitals.find().sort('number',-1).limit(1)
            for i in allhopitals:
                Num=i['number']+1
            
            item={"number":Num,
            "name":hospname,
            "lat":lat,
            "long":long,
            "key":pw,
            "city":city,
            "status":0,
            }
            case=3
            result=hospitals.insert_one(item)
            allhopitals=hospitals.find()
            return render_template("dashboard.html",info=allhopitals)
        except:
            message="An error was encountered. Please try again." 
            if case==0:
                message="The Pharmacy or City Name entered is not valid. Please try again."
            elif case==1:
                message="The Latitude and Longitude coordinates entered is/are not valid. Please try again."
            elif case==2:
                message="Something wrong with you password. Please try again."
            elif (case==3):
                message="There is something wrong at our end. Try again after sometime."
            return render_template("facility.html", msg=message)
    else:
        return newHospital()

@app.route('/show/')
def show():
    myhopitals=hospitals.find()
    allhopitals=[]
    for i in myhopitals:
        allhopitals = allhopitals + [i]
    return render_template("showcase.html", info=allhopitals)

if __name__=="__main__":
    app.run(debug=False)