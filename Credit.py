#initial set up: importing required modules
import numpy as np
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
import statsmodels.api as sm
import statsmodels.formula.api as smf

col_list = ['#cc615c', '#6965a7', '#f1bdbf']
sns.set_palette(col_list)

#importing data from credit.csv to dataframe, with an index on the 1st column
credit_df = pd.read_csv(path, index_col=0)
credit_df.head()

# we have 7 numeric and 4 object variables
# none of the variables have Null (or NaN) data values
credit_df.info()

#converting datatype categorical variables from object to category
credit_df.Gender = credit_df.Gender.astype('category')
credit_df.Student = credit_df.Student.astype('category')
credit_df.Married = credit_df.Married.astype('category')
credit_df.Ethnicity = credit_df.Ethnicity.astype('category')

credit_df.isnull().values.any()

# Describing numeric and categorical variables in the dataframe
credit_df.describe()

credit_df.describe(include=['category'])

sns.distplot(credit_df.Balance)
from scipy.stats import norm, skew

skewed_bal = skew(credit_df['Balance'])
print(skewed_bal)

# creating additional dataframe containing only the observations with a positive Balance
active_credit_df = credit_df.loc[credit_df.Balance>0,].copy()
active_credit_df.Balance.describe()

active_skewed_bal = skew(active_credit_df['Balance'])
print(active_skewed_bal)

# Creating a correlation matrix to visualize the relationships among the numerical predictors and the target of inference
numeric_credit_df = credit_df.select_dtypes(include=['int64', 'float64'])
plt.figure(figsize=(8,8))
plt.matshow(credit_df.corr(), cmap=plt.cm.Reds, fignum=1)
plt.colorbar()
tick_marks = [i for i in range(len(numeric_credit_df.columns))]
plt.xticks(tick_marks, numeric_credit_df.columns)
plt.yticks(tick_marks, numeric_credit_df.columns)

# checking correlation coefficients among variables from the above observations
from scipy.stats import pearsonr

r1, p1 = pearsonr(credit_df.Balance, credit_df.Limit)
msg = "Correlation coefficient Balance-Limit: {}\n p-value: {}\n"
print(msg.format(r1, p1))

r2, p2 = pearsonr(credit_df.Balance, credit_df.Rating)
msg = "Correlation coefficient Balance-Rating: {}\n p-value: {}\n"
print(msg.format(r2, p2))

r3, p3 = pearsonr(credit_df.Balance, credit_df.Income)
msg = "Correlation coefficient Balance-Income: {}\n p-value: {}\n"
print(msg.format(r3, p3))

r4, p4 = pearsonr(credit_df.Limit, credit_df.Rating)
msg = "Correlation coefficient Limit-Rating: {}\n p-value: {}\n"
print(msg.format(r4, p4))

r5, p5 = pearsonr(credit_df.Limit, credit_df.Income)
msg = "Correlation coefficient Limit-Income: {}\n p-value: {}\n"
print(msg.format(r5, p5))

r6, p6 = pearsonr(credit_df.Rating, credit_df.Income)
msg = "Correlation coefficient Rating-Income: {}\n p-value: {}\n"
print(msg.format(r6, p6))


# Limit and Rating have a high correlation coefficient causing multicollinearity
# Verifying the same by plotting data and regression line
# Collinearity issues can be fixed by removing either Rating or Limit. Rating determines Limit levels for card owners.
# Hence, we may exclude Limit while building model
sns.regplot(x='Limit', y='Rating', data=credit_df, line_kws={'color':'black'})


f, axes = plt.subplots(2, 2, figsize=(15, 6))
f.subplots_adjust(hspace=.3, wspace=.25)
credit_df.groupby('Gender').Balance.plot(kind='kde', ax=axes[0][0], legend=True, title='Balance by Gender')
credit_df.groupby('Student').Balance.plot(kind='kde', ax=axes[0][1], legend=True, title='Balance by Student')
credit_df.groupby('Married').Balance.plot(kind='kde', ax=axes[1][0], legend=True, title='Balance by Married')
credit_df.groupby('Ethnicity').Balance.plot(kind='kde', ax=axes[1][1], legend=True, title='Balance by Ethnicity')

# examining categorical variables and their relationship to target - Balance on active customers dataframe
f, axes = plt.subplots(2, 2, figsize=(15, 6))
f.subplots_adjust(hspace=.3, wspace=.25)
active_credit_df.groupby('Gender').Balance.plot(kind='kde', ax=axes[0][0], legend=True, title='Balance by Gender')
active_credit_df.groupby('Student').Balance.plot(kind='kde', ax=axes[0][1], legend=True, title='Balance by Student')
active_credit_df.groupby('Married').Balance.plot(kind='kde', ax=axes[1][0], legend=True, title='Balance by Married')
active_credit_df.groupby('Ethnicity').Balance.plot(kind='kde', ax=axes[1][1], legend=True, title='Balance by Ethnicity')

# Gender, Married, and Ethinicity features doesn't seem to influence Balance target variable
# However, Student seems to influence Balance target variable
# Examining Student variable using Box plot
sns.boxplot(x='Student', y='Balance', data = credit_df)

# Removed Limit feature in modelling
credit_df = credit_df.drop(columns = 'Limit')
active_credit_df = active_credit_df.drop(columns = 'Limit')
credit_df.head()
active_credit_df.head()
# creating a copy of the default dataframe, on which Label Encoding will be performed
encd_credit_df = credit_df.copy()
encd_credit_df.head()
# creating a copy of the active dataframe, on which Label Encoding will be performed
encd_active_credit_df = active_credit_df.copy()
encd_active_credit_df.head()

# Label Encoding of categorical variables of the default dataframe
lablel_encoder = LabelEncoder()
encd_credit_df['Gender'] = lablel_encoder.fit_transform(encd_credit_df['Gender'])
encd_credit_df['Student'] = lablel_encoder.fit_transform(encd_credit_df['Student'])
encd_credit_df['Married'] = lablel_encoder.fit_transform(encd_credit_df['Married'])
encd_credit_df['Ethnicity'] = lablel_encoder.fit_transform(encd_credit_df['Ethnicity'])

#Model 1: building 1st MLR model using all the predictors on the entire dataset
# making Independent and Dependent variables from the dataset
X1 = encd_credit_df.iloc[:,:-1]
y1 = encd_credit_df.Balance
# Fitting Multiple Linear Regression model
mod_mlr_default_all = LinearRegression()
mod_mlr_default_all.fit(X1, y1)
print(("intercept:", mod_mlr_default_all.intercept_))
print(("coefficients of predictors:", mod_mlr_default_all.coef_))
coeff = mod_mlr_default_all.coef_
coeff_mod_mlr_default_all = pd.DataFrame(coeff)
coeff_mod_mlr_default_all
print("Coefficient of Determination R-squared: ", mod_mlr_default_all.score(X1, y1)*100)


#Model 2 : building MLR model using all the predictors on the dataset having active customers¶
X2 = encd_active_credit_df.iloc[:,:-1]
y2 = encd_active_credit_df.Balance
mod_mlr_active_all = LinearRegression()
mod_mlr_active_all.fit(X2, y2)

print(("intercept:", mod_mlr_active_all.intercept_))
print(("coefficients of predictors:", mod_mlr_active_all.coef_))

coeff2 = mod_mlr_active_all.coef_
coeff_mod_mlr_active_all = pd.DataFrame(coeff2)
coeff_mod_mlr_active_all

print("Coefficient of Determination - R-squared: ", mod_mlr_active_all.score(X2, y2)*100)

'''Model 2 on active customers dataset seems to have a better fit compared to the 1st model. This means may be the non-active customers rarely make use of their credit card, and it is difficult to draw conclusions by including them.'''

# using statsmodel to find out p-value of each predictor
mod0 = smf.ols('Balance ~ Income + Rating + Cards + Age + Education + Gender + Student + Married + Ethnicity', data = encd_credit_df).fit()
mod0.summary()

# Using p-value, we can conclude that 'Income', 'Rating', 'Age', 'Student' are the significant features, which makes sense.
# Surprisingly, the years of education doesn't have much influence on predicting Balance target.
# we may build models by considering only the significant predictors


#Model 3: building MLR model using significant predictors on the entire dataset
X3 = encd_credit_df[['Income', 'Rating', 'Age', 'Student']].copy()
y3 = encd_credit_df.Balance
mod_mlr_default_sig = LinearRegression()
mod_mlr_default_sig.fit(X3, y3)

print(("intercept:", mod_mlr_default_sig.intercept_))
print(("coefficients of predictors:", mod_mlr_default_sig.coef_))

coeff3 = mod_mlr_default_sig.coef_
coeff_mod_mlr_default_sig = pd.DataFrame(coeff3)
coeff_mod_mlr_default_sig

print("Coefficient of Determination R-squared: ", mod_mlr_default_sig.score(X3, y3)*100)


# Model 4: building MLR model using significant predictors on the dataset having active customers
X4 = encd_active_credit_df[['Income', 'Rating', 'Age', 'Student']].copy()
y4 = encd_active_credit_df.Balance
mod_mlr_active_sig = LinearRegression()
mod_mlr_active_sig.fit(X4, y4)

print(("intercept:", mod_mlr_active_sig.intercept_))
print(("coefficients of predictors:", mod_mlr_active_sig.coef_))

coeff4 = mod_mlr_active_sig.coef_
coeff_mod_mlr_active_sig = pd.DataFrame(coeff4)
coeff_mod_mlr_active_sig

# checking R-squared for all the models together
print("------------ coefficient of determination R^2 ----------------")
print("\nMLR - default df - all predictors:         ", mod_mlr_default_all.score(X1, y1)*100)
print("MLR - default df - significant predictors: ", mod_mlr_default_sig.score(X3, y3)*100)
print("MLR - active df - all predictors:          ", mod_mlr_active_all.score(X2, y2)*100)
print("MLR - active df - significant predictors:  ", mod_mlr_active_sig.score(X4, y4)*100)

'''Although we used significant variables only, the R-squared has decreased. That means, we should analyze the relationships among these 4 variables.'''

f, axes = plt.subplots(3, 2, figsize=(12, 10))
f.subplots_adjust(hspace=.5, wspace=.25)
credit_df.groupby('Student').Income.plot(kind='kde', ax=axes[0][0], title='Income by Student', legend=True)
credit_df.groupby('Student').Rating.plot(kind='kde', ax=axes[0][1], title='Rating by Student', legend=True)
credit_df.plot(kind='scatter', x='Age' , y='Income' , ax=axes[1][0], title='Income and Age', legend=True)
credit_df.plot(kind='scatter', x='Age' , y='Rating' , ax=axes[1][1], color='orange', title='Rating and Age', legend=True)
credit_df.plot(kind='scatter', x='Rating' , y='Income' , ax=axes[2][0], color='orange', title='Income and Rating', legend=True)
credit_df.groupby('Student').Age.plot(kind='kde', ax=axes[2][1], legend=True, title='Age by Student')


'''Students have lower values of Income compared to non-Students
Surprisingly, Income does not Increase with Age
Positive relationship between Income and Rating
The Age of Students compared to non-Students does not differ significantly
Data quality may not be the best one'''
