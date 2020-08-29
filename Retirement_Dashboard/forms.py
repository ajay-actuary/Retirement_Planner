from django import forms
import datetime, calendar
# from material import *

class RetirementDashboardForm(forms.Form):
    AnnChoices = [('S0', 'No Spousal Annuity'),
               ('S50', '50% Spousal Annuity'),
               ('S100', '100% Spousal Annuity')
                  ]

    AccChoices = [('BH', 'Buy & Hold'),
               ('CM', 'Constant Mix')]

    GenderChoices = [('Male', 'Male'),
               ('Female', 'Female')]

    Age = forms.IntegerField(initial=30,min_value=18,max_value=50)
    Monthly_Salary = forms.IntegerField(initial=30000,min_value=0,label='Salary')
    Salary_Growth = forms.IntegerField(initial=8,min_value=-10,max_value=30,label='Pay Increase %')
    Contribution_Percent = forms.FloatField(initial=14,min_value=0,max_value=100,label='NPS Allocation %')
    Strategy =forms.ChoiceField(choices=AccChoices,required=True, initial='BH',label='')
    Equity_Percent = forms.FloatField(initial=34, min_value=0,label='Equity %')
    GSec_Percent = forms.FloatField(initial=33, min_value=0,label='GSec %')
    CorpBond_Percent = forms.FloatField(initial=33, min_value=0,label='CSec %')
    Gender_Type =forms.ChoiceField(choices=GenderChoices,required=True, initial='Male',label='')
    Annuity_Type =forms.ChoiceField(choices=AnnChoices,required=True, initial='S0',label='')

    def __init__(self, *args, **kwargs):
        super(RetirementDashboardForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control border-0 small form-inline'
            visible.field.widget.attrs['style'] = 'min-width: 70px; max-width: 120px ; margin-left: 10px; '

        self.fields['Equity_Percent'].widget.attrs['onchange'] = 'calculateCorpBondAllocation()'
        self.fields['GSec_Percent'].widget.attrs['onchange'] = 'calculateCorpBondAllocation()'
        self.fields['Annuity_Type'].widget.attrs['style'] = 'min-width: 70px; max-width: 180px ; margin-left: 10px; display: inline;  '
        self.fields['Strategy'].widget.attrs['style'] = 'min-width: 70px; max-width: 150px ; margin-left: 10px; display: inline;  '
        self.fields['Gender_Type'].widget.attrs['style'] = 'min-width: 70px; max-width: 150px ; margin-left: 10px; display: inline;  '

