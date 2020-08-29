from django.shortcuts import render, HttpResponse
from .forms import *
import numpy as np
import json
import pandas as pd
from django.http import JsonResponse
from Retirement_Planner.keyDefinitions import *
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def DashboardOutputView(request):
    if request.is_ajax():
        reqOutput = querydict_to_dict(request.POST)

        # Unspecified Input
        Salary_Growth = .08
        Retirement_Age = 60
        monthlySalGrowth = (1 + Salary_Growth) ** (1 / 12) - 1

        # Get Inputs
        Age = int(reqOutput['Age'])
        Monthly_Salary = int(reqOutput['Monthly_Salary'])
        Salary_Growth = float(reqOutput['Salary_Growth'])/100
        Contribution_Percent = float(reqOutput['Contribution_Percent'])/100
        Equity_Percent = float(reqOutput['Equity_Percent'])/100
        GSec_Percent = float(reqOutput['GSec_Percent'])/100
        CorpBond_Percent = float(reqOutput['CorpBond_Percent'])/100
        Annuity_Type = reqOutput['Annuity_Type']
        Strategy = reqOutput['Strategy']
        Gender_Type = reqOutput['Gender_Type']

        if Gender_Type == 'Male':
            Spousal_Age_Diff = -3
        else:
            Spousal_Age_Diff = 3

        if Annuity_Type == 'S0':
            Spousal_Benefit = 0
        elif Annuity_Type == 'S50':
            Spousal_Benefit = .5
        else:
            Spousal_Benefit = 1

        # Portfolio Mean & Volatility
        mu = Mean()
        sigma = Sigma()
        Allocation = np.array([CorpBond_Percent, Equity_Percent, GSec_Percent])
        monthlySalGrowth = (1 + Salary_Growth) ** (1 / 12) - 1

        # Load Saved Numpy Simulation
        np.random.seed(125698)
        Z = 1 + np.random.multivariate_normal(mu / 12, sigma / 12,((Retirement_Age - Age) * 12, 1000))  # done monthly
        Z1 = np.swapaxes(np.transpose(np.swapaxes(Z, 1, 2)), 1, 2)  # swap axis)

        if Strategy == 'BH':
            Z2 = np.cumproduct(Z1, 1)  # cumproduct by year by type

            # Flip Array
            Z3 = np.flip(Z2, 1)  # accumulating factor by year

            # Salary Growth
            Z4 = np.cumproduct((1 + monthlySalGrowth) * np.ones([np.size(Z3, 0), np.size(Z3, 1), np.size(Z3, 2)]), 1)
            Z5 = np.multiply(Z3, Z4)
            Z6 = np.sum(Z5, 1)
            PortfolioSeries = np.sum(np.multiply(Z6,Allocation),axis=1)*Monthly_Salary*Contribution_Percent
        else:
            Z2 = np.cumproduct(np.sum(np.multiply(Z1, Allocation), axis=2), 1)
            Z3 = np.flip(Z2, 1)  # accumulating factor by year
            Z4 = np.cumproduct((1 + monthlySalGrowth) * np.ones([np.size(Z3, 0), np.size(Z3, 1)]), 1)
            Z5 = np.multiply(Z3, Z4)
            Z6 = np.sum(Z5, 1)
            PortfolioSeries = Z6 * Monthly_Salary * Contribution_Percent

        Stressed_Estimate = np.percentile(PortfolioSeries,5)
        Pessimistic_Estimate = np.percentile(PortfolioSeries,25)
        Likely_Estimate = np.percentile(PortfolioSeries,50)
        Optimistic_Estimate = np.percentile(PortfolioSeries,75)
        Overtly_Optimistic_Estimate =  np.percentile(PortfolioSeries,95)

        Monthly_Estimate = int(Monthly_Salary*((1+monthlySalGrowth)**((Retirement_Age - Age)*12)))

        ## Calculate Annuity Rate
        Annuity_Rate = 1/annuityCalculator(Data=mortalityData(), intRate=mu[2]-(.7/100), spouseAgeDiff=Spousal_Age_Diff,
                                         spousalBenefit=Spousal_Benefit,Type=Annuity_Type)
        Annuity_Estimate = int(Likely_Estimate*Annuity_Rate/12)

        Stressed_Estimate = round(100*Stressed_Estimate*Annuity_Rate/(12*Monthly_Estimate),1)
        Pessimistic_Estimate = round(100*Pessimistic_Estimate*Annuity_Rate/(12*Monthly_Estimate),1)
        Likely_Estimate = round(100*Likely_Estimate*Annuity_Rate/(12*Monthly_Estimate),1)
        Optimistic_Estimate = round(100*Optimistic_Estimate*Annuity_Rate/(12*Monthly_Estimate),1)
        Overtly_Optimistic_Estimate = round(100*Overtly_Optimistic_Estimate*Annuity_Rate/(12*Monthly_Estimate),1)

        Portfolio_Mean = int(np.sum(np.multiply(Allocation,mu))*10000)/100
        Portfolio_Sigma = ((np.dot(Allocation, np.dot(sigma, Allocation.T)))**.5)*100
        Accumulation_PV = int(np.percentile(PortfolioSeries, 50) / ((1 + mu[2]) ** (Retirement_Age - Age - .5)))

        # Tail Value at Risk at 95%
        tVAR = np.mean(PortfolioSeries) - np.mean(PortfolioSeries[PortfolioSeries.argsort()[:int(len(PortfolioSeries)*.05)]])
        tVAR_PV = tVAR/((1+mu[2])**(Retirement_Age-Age-.5))

        # Replacement at 50%
        Replacement_Shortfall_Rate = max(.5 - Likely_Estimate/100 ,0)
        Replacement_Shortfall = 12*Replacement_Shortfall_Rate*Monthly_Estimate/(Annuity_Rate)
        Replacement_Shortfall_PV = Replacement_Shortfall/((1+mu[2])**(Retirement_Age-Age-.5))

        # Chart data for Bar Chart
        chart_annuity_pctl_data = []
        for x in range(5,100,10):
            chart_annuity_pctl_data += [int(np.percentile(PortfolioSeries,x)*Annuity_Rate/(12))]

        # chart_annuity_pctl_data = [0, 10000, 5000, 15000, 10000, 20000, 15000, 25000, 20000, 30000, 10000]

        # Read Efficient Frontier Data
        effFrontier = EfficientFrontier()
        effFrontier = pd.DataFrame(data=effFrontier,
                                   columns=["CorpBonds", "Equity", "GSec", "Mean", "StDev", "Efficient"])
        effFrontier.sort_values(by=['Mean'], inplace=True)

        effFrontier_all = effFrontier.copy()
        effFrontier = effFrontier_all.loc[effFrontier_all['Efficient']==1,:].reset_index(drop=True)
        effFrontier['Label'] = ' (Equity : ' + effFrontier["Equity"].astype(int).astype(str) + \
                               ', GSec : ' + effFrontier["GSec"].astype(int).astype(str) + \
                               ' , CorpBonds : ' + effFrontier["CorpBonds"].astype(int).astype(str) + ')'
        effFrontier_Label = effFrontier['Label'].tolist()

        # Efficient Frontier
        effFrontier_List = []
        for h, w in zip(effFrontier['StDev'].tolist(), effFrontier['Mean'].tolist()):
            effFrontier_List.append({'x': h, 'y': w})

        # Current Portfolio
        effFrontier_all_List = [{'x': Portfolio_Sigma, 'y': Portfolio_Mean}]

        stmnt1 = ['Alternatively, you can invest Rs.{0} today in safe securities<br><br> '
                               .format('{:,.0f}'.format(Replacement_Shortfall_PV)) if Replacement_Shortfall > 0 else ''][0]

        ###### Summary Text #####
        Advice = ''' You are <font color="darkred"><b>{0}</b></font> saving enough for a comfortable retirement <br><br>     
                     You are expected to recieve <b>{1}%</b> of your final salary every month as pension after retirement. 
                     Your spouse will recieve {7}% of your final salary, should they outlive you <br><br>
                     You will need to contribute at least {2}% of your monthly salary to NPS to buy an old age pension of
                        50% of your final salary. You are now contributing {6}%  <br><br>
                    {5}
                    This advice is based on a long term salary growth projection of {3}% and annuity rate projection of {4}%
                    '''.format(['' if Likely_Estimate > 50 else 'not'][0],
                               round(100*Annuity_Estimate/Monthly_Estimate,1),
                               round(100*Contribution_Percent*50/Likely_Estimate,1),
                               round(Salary_Growth*100,1),
                               round(Annuity_Rate*100,1),
                               stmnt1,
                               int(100*Contribution_Percent)
                               ,[0 if Annuity_Type == 'SLA' else round(Spousal_Benefit*100*Annuity_Estimate/Monthly_Estimate,1)][0])


        # Max return for same risk
        effFilter = effFrontier.copy()
        effFilter = effFilter.query('Mean > {0} and StDev < {1}'.format(Portfolio_Mean,Portfolio_Sigma))
        if len(effFilter) > 1:
            minRiskPortfolio = effFilter.copy().sort_values(['Mean'],ascending=False)
            maxReturnPortfolio = effFilter.copy().sort_values(['StDev'], ascending=True)

            EffAdviceAdd = '''
            You can get a higher return {0}% for the similar risk level by changing it to {1}<br><br>
            Or you can get the similar return for a lower risk {2}%  by changing it to {3}<br><br>
            '''.format('{:,.1f}'.format(maxReturnPortfolio['Mean'].tolist()[0]),
                       maxReturnPortfolio['Label'].tolist()[0],
                       '{:,.1f}'.format(minRiskPortfolio['StDev'].tolist()[0]),
                       minRiskPortfolio['Label'].tolist()[0])
        else:
            EffAdviceAdd = ''

        # Min risk for same return
        EffAdvice = '''Your portfolio is currently invested in (Equity: {0}%, CorpBonds : {1}%, GSec : {2}%)<br><br>
                       This is <font color="darkred"><b>{3}</b></font> a near efficient portfolio <br><br>   
                       {4}                   
                    '''.format(Equity_Percent*100,GSec_Percent*100,CorpBond_Percent*100,
                               ['not' if len(effFilter) > 1 else ''][0],
                               EffAdviceAdd
                               )

        return JsonResponse({'Stressed_Estimate':Stressed_Estimate,
                 'Pessimistic_Estimate': Pessimistic_Estimate,
                 'Likely_Estimate': Likely_Estimate,
                 'Optimistic_Estimate': Optimistic_Estimate,
                 'Overtly_Optimistic_Estimate': Overtly_Optimistic_Estimate,
                 'Monthly_Estimate': '{:,.0f}'.format(Monthly_Estimate),
                 'Annuity_Estimate': '{:,.0f}'.format(Annuity_Estimate),
                 'Portfolio_Mean' : '{:,.2f}'.format(Portfolio_Mean),
                 'Portfolio_Sigma': '{:,.2f}'.format(Portfolio_Sigma),
                 'Accumulation_PV': '{:,.0f}'.format(Accumulation_PV),
                 'tVAR': '{:,.0f}'.format(tVAR),
                 'tVAR_PV':  '{:,.0f}'.format(tVAR_PV),
                 'Replacement_Shortfall': '{:,.0f}'.format(Replacement_Shortfall),
                 'Replacement_Shortfall_PV':'{:,.0f}'.format(Replacement_Shortfall_PV),
                 'chart_annuity_pctl_data': chart_annuity_pctl_data,
                 'effFrontier_json':effFrontier_List,
                 'effFrontier_all_json':effFrontier_all_List,
                 'effFrontier_Label': effFrontier_Label,
                 'Advice':Advice,
                 'EffAdvice': EffAdvice,
                 'is_taken': True
                 },safe=False)

@csrf_protect
def DashboardView(request):
    form = RetirementDashboardForm()

    return render(request, 'static/index.html', {'form': form})