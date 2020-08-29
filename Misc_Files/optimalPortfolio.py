import pandas as pd
import numpy as np

path = '/home/ajay/Documents/Actuarial/2020_RM_Project/'

# Load Saved Mean & Covariance Matrix
mu = np.load(path+'/Copula_Array/stat_mean.npy')
sigma = np.load(path+'/Copula_Array/stat_sigma.npy')

# Get Scenarios
Combinations = np.array(np.meshgrid(range(0,110,10), range(0,110,10), range(0,110,10))).T.reshape(-1,3) 

# take only cases with sum of allocation = 100
CombinationsFiltered = Combinations[np.sum(Combinations,axis=1) == 100] 

# Calculate Mean & Std Dev
Output = np.zeros([np.size(CombinationsFiltered,0),3])

for x in range(len(CombinationsFiltered)):
    Allocation = CombinationsFiltered[x]
    Output[x,0] = np.sum(np.multiply(Allocation,mu))
    Output[x,1] = (np.dot(Allocation, np.dot(sigma, Allocation.T)))**.5

Output[:,0] = np.round_(Output[:,0],1)
# Calculate Efficient Frontier
for x in range(len(Output)):
   Output[x,2] = np.count_nonzero((Output[:,0] >= Output[x,0])*(Output[:,1] < Output[x,1])) == 0
   
Output = np.hstack((CombinationsFiltered,Output))

# Create Pandas Dataframe
# effFrontier = pd.DataFrame(data=Output, columns=["CorpBonds", "Equity","GSec","Mean","StDev","Efficient"])

# np.save(path+'/Copula_Array/'+'effFrontier',Output)

# effFrontier.to_excel(path+'Efficient_Frontier.xlsx',index=False)