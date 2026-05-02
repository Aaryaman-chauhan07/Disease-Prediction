from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import numpy as np
import os
import pandas as pd
import string
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import seaborn as sns
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from string import punctuation
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.neighbors import KNeighborsClassifier
from numpy import dot
from numpy.linalg import norm
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

global uname, tfidf_vectorizer, scaler
global X_train, X_test, y_train, y_test
accuracy, precision, recall, fscore = [], [], [], []

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def cleanData(doc):
    tokens = doc.split()
    table = str.maketrans('', '', punctuation)
    tokens = [w.translate(table) for w in tokens]
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w in stop_words]
    tokens = [word for word in tokens if len(word) > 1]
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    tokens = ' '.join(tokens)
    return tokens

dataset = pd.read_csv('Dataset/dataset.csv', encoding ="ISO-8859-1")
labels = dataset['Source'].unique().tolist()
symptoms = dataset.Target
diseases = dataset.Source
Y = []
for i in range(len(diseases)):
    index = labels.index(diseases[i])
    Y.append(index)

X = []
for i in range(len(symptoms)):
    arr = symptoms[i]
    arr = arr.strip().lower()
    arr = arr.replace("_", " ")
    X.append(cleanData(arr))
vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
tfidf = vectorizer.fit_transform(X).toarray()        
X = pd.DataFrame(tfidf, columns=vectorizer.get_feature_names_out())  
Y = np.asarray(Y)
X = X.values
indices = np.arange(X.shape[0])
np.random.shuffle(indices)
X = X[indices]
Y = Y[indices]
#scaler = StandardScaler()
#X = scaler.fit_transform(X)
print(X)
print(X.shape)
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2) #split data into train & test

def calculateMetrics(algorithm, predict, y_test):
    global accuracy, precision, recall, fscore
    a = accuracy_score(y_test,predict)*100
    p = precision_score(y_test, predict,average='macro') * 100
    r = recall_score(y_test, predict,average='macro') * 100
    f = f1_score(y_test, predict,average='macro') * 100
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)

knn = KNeighborsClassifier(n_neighbors=15)
knn.fit(X_train, y_train)
predict = knn.predict(X_test)
calculateMetrics("KNN", predict, y_test)

# Train Gradient Boosting Decision Tree
gbdt = GradientBoostingClassifier()
gbdt.fit(X_train, y_train)
predict = gbdt.predict(X_test)
calculateMetrics("GBDT", predict, y_test)


rf = RandomForestClassifier()
rf.fit(X_train, y_train)
predict = rf.predict(X_test)
calculateMetrics("Random Forest", predict, y_test)



def PredictDisease(request):
    if request.method == 'GET':
       return render(request, 'PredictDisease.html', {})

def getMedicines(disease):
    dis = disease.lower()
    prescription = "Unable to prescribed medicines for given disease"
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * from medicines")
        rows = cur.fetchall()
        for row in rows:
            data = row[0].lower()
            if dis in data:
                prescription = row[1]
                break
    return prescription            
    

def PredictAction(request):
    if request.method == 'POST':
        global scaler, rf, vectorizer, labels
        symptoms = request.POST.get('t1', False)
        arr = symptoms.strip().lower()
        testData = vectorizer.transform([cleanData(arr)]).toarray()
        #testData = scaler.transform(testData)
        predict = rf.predict(testData)[0]
        predict = int(predict)
        output = labels[predict]
        data = '<font size="3" color="blue">Symptoms = '+symptoms+'<br/>Predicted Disease : '+output+"</font><br/>"
        data += '<font size="3" color="blue">Recommended Medicines = '+getMedicines(output)
        context= {'data':data}
        return render(request, 'PredictDisease.html', context)

def TrainML(request):
    if request.method == 'GET':
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="" color="black">Algorithm Name</th><th><font size="" color="black">Accuracy</th><th><font size="" color="black">Precision</th>'
        output+='<th><font size="" color="black">Recall</th><th><font size="" color="black">FSCORE</th></tr>'
        global accuracy, precision, recall, fscore
        algorithms = ['KNN', 'GBDT']
        for i in range(len(algorithms)):
            output+='<td><font size="" color="black">'+algorithms[i]+'</td><td><font size="" color="black">'+str(accuracy[i])+'</td><td><font size="" color="black">'+str(precision[i])+'</td><td><font size="" color="black">'+str(recall[i])+'</td><td><font size="" color="black">'+str(fscore[i])+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def Aboutus(request):
    if request.method == 'GET':
       return render(request, 'Aboutus.html', {})

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        
        status = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select username from signup where username = '"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == email:
                    status = 'Given Username already exists'
                    break
        if status == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'diseasediagnosis',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(username,password,contact_no,email_id,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = 'Signup Process Completed'
        context= {'data':status}
        return render(request, 'Signup.html', context)

def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        option = 0
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM signup")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    uname = username
                    option = 1
                    break
        if option == 1:
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'UserLogin.html', context)

def AdminLoginAction(request):
    if request.method == 'POST':
        global uname
        option = 0
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == "admin" and password == "admin":
            context= {'data':'welcome '+username}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'AdminLogin.html', context)          

def AddHospitals(request):
    if request.method == 'GET':
        global diseases
        output = '<tr><td><font size="" color="black">Speciality</b></td><td><select name="t2" multiple>'
        unique = np.unique(diseases)
        for i in range(len(unique)):
            output += '<option value="'+unique[i]+'">'+unique[i]+'</option>'
        output += '</select></td></tr>'
        context= {'data1':output}
        return render(request, 'AddHospitals.html', context)

def AddPharmacy(request):
    if request.method == 'GET':
        return render(request, 'AddPharmacy.html', {})

def AddDiagnostic(request):
    if request.method == 'GET':
        return render(request, 'AddDiagnostic.html', {})

def AddPrescription(request):
    if request.method == 'GET':
        return render(request, 'AddPrescription.html', {})

def AddPrescriptionAction(request):
    if request.method == 'POST':
        global uname
        disease = request.POST.get('t1', False)
        medicines = request.POST.get('t2')
        
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO medicines(disease,medicines) VALUES('"+disease+"','"+medicines+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = 'Prescription details added'
        context= {'data':status}
        return render(request, 'AddPrescription.html', context)    

def AddHospitalsAction(request):
    if request.method == 'POST':
        global uname
        hospital = request.POST.get('t1', False)
        speciality = request.POST.getlist('t2')
        speciality = ','.join(speciality)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        lat = request.POST.get('t6', False)
        lon = request.POST.get('t7', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO hospitals(hospital_name,specialities,contact_no,email,address,latitude,longitude) VALUES('"+hospital+"','"+speciality+"','"+contact+"','"+email+"','"+address+"','"+lat+"','"+lon+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = 'Hospital details added'
        context= {'data':status}
        return render(request, 'AdminScreen.html', context)        

def AddPharmacyAction(request):
    if request.method == 'POST':
        pharmacy = request.POST.get('t1', False)
        desc = request.POST.get('t2')
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        lat = request.POST.get('t6', False)
        lon = request.POST.get('t7', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO pharmacy(pharmacy_name,description,contact_no,email,address,latitude,longitude) VALUES('"+pharmacy+"','"+desc+"','"+contact+"','"+email+"','"+address+"','"+lat+"','"+lon+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = 'Pharmacy details added'
        context= {'data':status}
        return render(request, 'AddPharmacy.html', context)      

def AddDiagnosticAction(request):
    if request.method == 'POST':
        diagnostic = request.POST.get('t1', False)
        desc = request.POST.get('t2')
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        lat = request.POST.get('t6', False)
        lon = request.POST.get('t7', False)
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO diagnostic(diagnostoc_name,description,contact_no,email,address,latitude,longitude) VALUES('"+diagnostic+"','"+desc+"','"+contact+"','"+email+"','"+address+"','"+lat+"','"+lon+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        print(db_cursor.rowcount, "Record Inserted")
        if db_cursor.rowcount == 1:
            status = 'Diagnostic details added'
        context= {'data':status}
        return render(request, 'AddDiagnostic.html', context)

def ViewHospitals(request):
    if request.method == 'GET':
        output = '<table border=1><tr><th><font size="" color=black>Hospital Name</font></th>'
        output+='<td><font size="" color="black">Disease Speciality</td>'
        output+='<td><font size="" color="black">Contact No</td>'
        output+='<td><font size="" color="black">Email</td>'
        output+='<td><font size="" color="black">Address</td>'
        output+='<td><font size="" color="black">Latitude</td>'
        output+='<td><font size="" color="black">Longitude</td>'
        output+='<td><font size="" color="black">View on Map</td></tr>'
        rank = []
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM hospitals")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="" color="black">'+str(row[0])+'</td>'
                output+='<td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td>'
                output+='<td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td>'
                output+='<td><font size="" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="" color="black">'+str(row[6])+'</td>'
                output+='<td><a href=\'ViewMap?t1='+str(row[0])+'\'><font size=3 color=black>View on Map</font></a></td></tr>'                
        output += "</table><br/><br/><br/>"
        context= {'data': output}
        return render(request, 'UserScreen.html', context)

def ViewMap(request):
    if request.method == 'GET':
        name = request.GET.get('t1', False)
        output = '<iframe width="625" height="650" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?q='+name+'&amp;ie=UTF8&amp;&amp;output=embed"></iframe><br/>'
        context= {'data':output}
        return render(request, 'Map.html', context)    

def ViewPharmacy(request):
    if request.method == 'GET':
        output = '<table border=1><tr><th><font size="" color=black>Pharmacy Name</font></th>'
        output+='<td><font size="" color="black">Description</td>'
        output+='<td><font size="" color="black">Contact No</td>'
        output+='<td><font size="" color="black">Email</td>'
        output+='<td><font size="" color="black">Address</td>'
        output+='<td><font size="" color="black">Latitude</td>'
        output+='<td><font size="" color="black">Longitude</td>'
        output+='<td><font size="" color="black">View on Map</td></tr>'
        rank = []
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM pharmacy")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="" color="black">'+str(row[0])+'</td>'
                output+='<td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td>'
                output+='<td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td>'
                output+='<td><font size="" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="" color="black">'+str(row[6])+'</td>'
                output+='<td><a href=\'ViewMap?t1='+str(row[0])+'\'><font size=3 color=black>View on Map</font></a></td></tr>'                
        output += "</table><br/><br/><br/>"
        context= {'data': output}
        return render(request, 'UserScreen.html', context)    

def ViewDiagnostic(request):
    if request.method == 'GET':
        output = '<table border=1><tr><th><font size="" color=black>Diagnostic Name</font></th>'
        output+='<td><font size="" color="black">Description</td>'
        output+='<td><font size="" color="black">Contact No</td>'
        output+='<td><font size="" color="black">Email</td>'
        output+='<td><font size="" color="black">Address</td>'
        output+='<td><font size="" color="black">Latitude</td>'
        output+='<td><font size="" color="black">Longitude</td>'
        output+='<td><font size="" color="black">View on Map</td></tr>'
        rank = []
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = '', database = 'diseasediagnosis',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM diagnostic")
            rows = cur.fetchall()
            for row in rows:
                output+='<tr><td><font size="" color="black">'+str(row[0])+'</td>'
                output+='<td><font size="" color="black">'+str(row[1])+'</td>'
                output+='<td><font size="" color="black">'+str(row[2])+'</td>'
                output+='<td><font size="" color="black">'+str(row[3])+'</td>'
                output+='<td><font size="" color="black">'+str(row[4])+'</td>'
                output+='<td><font size="" color="black">'+str(row[5])+'</td>'
                output+='<td><font size="" color="black">'+str(row[6])+'</td>'
                output+='<td><a href=\'ViewMap?t1='+str(row[0])+'\'><font size=3 color=black>View on Map</font></a></td></tr>'                
        output += "</table><br/><br/><br/>"
        context= {'data': output}
        return render(request, 'UserScreen.html', context)


    
