from flask import Flask, render_template, request, current_app,session,redirect, url_for
from flask_login import current_user,login_required,LoginManager,login_user
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import pandas as pd
import pickle,joblib
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = "^A%DJAJU^JJ123"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lp3'
mysql = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/analysis')
def analysis():
  if 'loggedin' in session:
    return render_template("analysis.html")
  else:
    return redirect(url_for('login'))
 

@app.route('/form')
def form():
  if 'loggedin' in session:
    return render_template("index1.html")
  else:
    return redirect(url_for('login'))


@app.route('/')
def dashboard():
  return render_template("index.html")


@app.route('/result', methods=['GET', 'POST'])
def result():
    if 'loggedin' in session:
      if request.method == 'POST':
          age = request.form['age']
          gen = request.form['gen']
          edu = request.form.get('edu')
          mi = request.form.get('mi')
          pr1 = request.form.get('pr1')
          rs = request.form.get('rs')
          edf = request.form.get('edf')
          mars = request.form.get('mars')


          envs = request.form.get('envs')
          joi = request.form.get('joi')
          jole = request.form.get('jole')
          jos = request.form.get('jos')
          ncom = request.form['ncom']
          jobr = request.form['jobr']
          persal = request.form.get('persal')
          stpl = request.form.get('stpl')
          totw = request.form.get('totw')
          dept = request.form.get('dept')
          train = request.form.get('train')
          wrkbal = request.form.get('wrkbal')
          yrs = request.form.get('yrs')
          yrscurr = request.form.get('yrscurr')
          yrsprom = request.form.get('yrsprom')
          yrsman = request.form.get('yrsman')
          ovtime = request.form.get('ovtime')

          dr = request.form.get('dr')
          hr = request.form.get('hr')
          mr = request.form.get('mr')
          bt = request.form.get('bt')
          dfh = request.form['dfh']   

          attrition = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")

          attrition.drop(['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours'], axis="columns", inplace=True)

          from sklearn.preprocessing import LabelEncoder

          label = LabelEncoder()
          attrition["Attrition"] = label.fit_transform(attrition.Attrition)

          target_map = {1 : 'Yes', 0: 'No'}
          # Use the pandas apply method to numerically encode our attrition target variable
          attrition["Attrition"] = attrition["Attrition"].apply(lambda x: target_map[x])

          # Define a dictionary for the target mapping
          target_map = {'Yes':1, 'No':0}
          # Use the pandas apply method to numerically encode our attrition target variable
          attrition["Attrition_numerical"] = attrition["Attrition"].apply(lambda x: target_map[x])

          attrition = attrition.drop(['Attrition_numerical'], axis=1)

          # Empty list to store columns with categorical data
          categorical = []
          for col, value in attrition.iteritems():
          
              if value.dtype == 'object':
                  categorical.append(col)

          attrition_cat = attrition[categorical]
          attrition_cat = attrition_cat.drop(['Attrition'], axis=1)
          temp_attrition_cat = attrition_cat
          input_array = [int(age), int(dr), int(dfh), int(edu), int(envs), int(hr), int(joi), int(jole), int(jos), int(mi), int(mr), int(ncom), int(persal), int(pr1), int(rs), int(stpl), int(totw), int(train), int(wrkbal), int(yrs), int(yrscurr), int(yrsprom), int(yrsman),bt, dept, edf, gen, jobr, mars, ovtime]
          input_numerical = input_array[0:23]
          input_categorical = input_array[23:]
          input_categorical = [input_categorical] 
          input_df = pd.DataFrame(input_categorical, columns = ['BusinessTravel','Department','EducationField', 'Gender', 'JobRole', 'MaritalStatus', 'OverTime'])
          temp_attrition_cat = temp_attrition_cat.append(input_df, ignore_index=True)
          temp_attrition_cat = pd.get_dummies(temp_attrition_cat)
          final_input_cat = temp_attrition_cat[-1:]
          numerical_columns = ['Age', 'DailyRate',    'DistanceFromHome', 'Education',    'EnvironmentSatisfaction',  'HourlyRate',   'JobInvolvement',   'JobLevel', 'JobSatisfaction',  'MonthlyIncome',    'MonthlyRate','NumCompaniesWorked', 'PercentSalaryHike',    'PerformanceRating',    'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',    'TrainingTimesLastYear' ,'WorkLifeBalance', 'YearsAtCompany',   'YearsInCurrentRole',   'YearsSinceLastPromotion'   ,'YearsWithCurrManager']
          input_num_df = pd.DataFrame([input_numerical], columns = numerical_columns)
          input_num_df.reset_index(drop=True, inplace=True)
          final_input_cat.reset_index(drop=True, inplace=True)
          input_final = pd.concat([input_num_df, final_input_cat], axis=1)
          picklfile=joblib.load('logistic_model.pkl')
          resultf=picklfile.predict(input_final)
          print('done')
          return render_template('result.html',var1=resultf)
      else:
        return render_template('result.html',var1=[1]) 
    else:
      redirect(url_for('login'))      

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        hashpassword=sha256_crypt.hash(str(password))
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cursor.fetchone()
        cursor.close()
        if len(account) > 0:
            if sha256_crypt.verify(password,account['password']):
                session['name'] = account['email']
                session['id'] = account['id']
                session['loggedin'] = True
                return render_template("index1.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    if request.method=='GET':
      return render_template("index.html")
    else:
        return render_template("index.html")

@app.route('/logout')
def logout():
    session.pop('name',None)
    session.pop('id',None)
    session.pop('loggedin',None)
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
      app.run(debug=False,port=7000)