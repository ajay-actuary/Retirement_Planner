import pandas as pd
import numpy as np
from scipy.linalg import cholesky

path = '/home/ajay/Documents/Actuarial/2020_RM_Project/Retirement_Planner/Misc_Files/'
Simulations = 10000

# Read Data
Data = pd.read_excel(path+'NAV_Data.xlsx')

Data['Type'] = Data['Name'].apply(lambda x: 'Equity' if '-e-tier-i' in x and x.split('-')[-1] != 'ii' else
                                  'Corp' if '-c-tier-i' in x  and x.split('-')[-1] != 'ii' else
                                  'GSec' if '-g-tier-i' in x  and x.split('-')[-1] != 'ii' 
                                  else 'OTHER')
Data = Data.loc[Data['Type']!='OTHER',:]
Data1 = Data.groupby(['Type','Date'])['Returns'].mean().reset_index()

Data2 = Data1.pivot_table(values='Returns', index='Date', columns='Type', aggfunc='first').reset_index()
Data2['Date'] = Data2['Date'].apply(lambda x: x.date())

Data3 = Data2.where(pd.notnull(Data2), None).dropna().reset_index(drop=True)
Data3['Year'] = Data3['Date'].apply(lambda x: x.year)

#Data3.to_excel(path+'Summary_Data1.xlsx',index=False)

# Inputs
Salary_Growth = .08
Annuity_Rate = .07
Retirement_Age = 60
Equity_Percent = .34
GSec_Percent = .33
CorpBond_Percent = .33
Monthly_Salary = 14000
Contribution_Percent = .14
        
# Annualized Mean, StDev by asset class
statData = Data.groupby('Type').agg(mean=('Returns', 'mean'), std=('Returns', 'std'))
statData.reset_index(inplace=True)

# Change mean and stdev of portfolio
Ann_Days = len(Data3.loc[Data3['Year'] == 2019,:])
statData.iloc[0,1:3] = (.08/Ann_Days,.08/Ann_Days**.5 ) # Corp bonds mean & stdev changed to 8% each
statData.iloc[2,1] = (.065/Ann_Days) # GSec bonds mean changed to 6.5%


statData['Mean_Annualized'] = statData['mean']*Ann_Days
statData['StDev_Annualized'] = statData['std']*(Ann_Days**.5)


# Corr among asset classes & doing cholesky decomposition
corrMatrix = cholesky(Data2.loc[:,['Corp','Equity','GSec']].corr(method='pearson'),lower=True)

# Final Salary

# Simulate Copula
mu = statData['Mean_Annualized'].to_numpy()
s = statData['StDev_Annualized'].to_numpy()
#s = invgamma.pdf(df/2,df/2) 

np.random.seed(0)

# Get Seed of Ages
Allocation = np.array([CorpBond_Percent, Equity_Percent, GSec_Percent])
Age = 30
Z = 1 + np.random.multivariate_normal(mu/12, corrMatrix*(s*s/12),((Retirement_Age - Age)*12,1000)) # done monthly
Z1 = np.swapaxes(np.transpose(np.swapaxes(Z,1,2)),1,2) # swap axis)
Z2 = np.cumproduct(Z1,1) # cumproduct by year by type
# Flip Array
Z3 = np.flip(Z2,1) # accumulating factor by year

# Salary Growth
monthlySalGrowth = (1+Salary_Growth)**(1/12)-1
Z4 = np.cumproduct((1+monthlySalGrowth)*np.ones([np.size(Z3,0),np.size(Z3,1),np.size(Z3,2)]),1)
Z5 = np.multiply(Z3,Z4)
Z6 = np.sum(Z5,1)

# Constant Mix
Z21 = np.cumproduct(np.sum(np.multiply(Z1,Allocation),axis=2),1)
Z31 = np.flip(Z21,1) # accumulating factor by year
Z41 = np.cumproduct((1+monthlySalGrowth)*np.ones([np.size(Z31,0),np.size(Z31,1)]),1)

# np.save(path+'/Copula_Array/'+str(int(Age)),Z6)
    
# Save Mean, StDev
# np.save(path+'/Copula_Array/'+'stat_mean',mu)
# np.save(path+'/Copula_Array/'+'stat_sigma',corrMatrix*(s*s))

