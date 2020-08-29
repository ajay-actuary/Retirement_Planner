import pandas as pd
import numpy as np

def Mean():
    return np.array([0.08, 0.09297013, 0.065])

def Sigma():
    return np.array([[0.0064, 0., 0.],
              [0.00128168, 0.02640869, 0.],
              [0.00401064, -0.00135914, 0.00141722]])

def querydict_to_dict(query_dict):
    data = {}
    for key in query_dict.keys():
        v = query_dict.getlist(key)
        if len(v) == 1:
            v = v[0]
        data[key] = v
    return data

def mortalityData():
    return '''[{"Age":21,"lx":100000},{"Age":22,"lx":99904},{"Age":23,"lx":99804},
            {"Age":24,"lx":99701},{"Age":25,"lx":99595},{"Age":26,"lx":99486},
            {"Age":27,"lx":99375},{"Age":28,"lx":99263},{"Age":29,"lx":99149},
            {"Age":30,"lx":99034},{"Age":31,"lx":98919},{"Age":32,"lx":98803},
            {"Age":33,"lx":98687},{"Age":34,"lx":98571},{"Age":35,"lx":98453},
            {"Age":36,"lx":98330},{"Age":37,"lx":98201},{"Age":38,"lx":98065},
            {"Age":39,"lx":97920},{"Age":40,"lx":97764},{"Age":41,"lx":97596},
            {"Age":42,"lx":97414},{"Age":43,"lx":97214},{"Age":44,"lx":96996},
            {"Age":45,"lx":96761},{"Age":46,"lx":96509},{"Age":47,"lx":96236},
            {"Age":48,"lx":95937},{"Age":49,"lx":95607},{"Age":50,"lx":95242},
            {"Age":51,"lx":94838},{"Age":52,"lx":94390},{"Age":53,"lx":93882},
            {"Age":54,"lx":93313},{"Age":55,"lx":92685},{"Age":56,"lx":91999},
            {"Age":57,"lx":91257},{"Age":58,"lx":90462},{"Age":59,"lx":89612},
            {"Age":60,"lx":88704},{"Age":61,"lx":87737},{"Age":62,"lx":86709},
            {"Age":63,"lx":85690},{"Age":64,"lx":84651},{"Age":65,"lx":83565},
            {"Age":66,"lx":82404},{"Age":67,"lx":81136},{"Age":68,"lx":79755},
            {"Age":69,"lx":78231},{"Age":70,"lx":76546},{"Age":71,"lx":74686},
            {"Age":72,"lx":72639},{"Age":73,"lx":70397},{"Age":74,"lx":67957},
            {"Age":75,"lx":65321},{"Age":76,"lx":62494},{"Age":77,"lx":59488},
            {"Age":78,"lx":56320},{"Age":79,"lx":53010},{"Age":80,"lx":49585},
            {"Age":81,"lx":46074},{"Age":82,"lx":42511},{"Age":83,"lx":38931},
            {"Age":84,"lx":35372},{"Age":85,"lx":31871},{"Age":86,"lx":28464},
            {"Age":87,"lx":25187},{"Age":88,"lx":22071},{"Age":89,"lx":19143},
            {"Age":90,"lx":16426},{"Age":91,"lx":13937},{"Age":92,"lx":11686},
            {"Age":93,"lx":9678},{"Age":94,"lx":7912},{"Age":95,"lx":6382},
            {"Age":96,"lx":5075},{"Age":97,"lx":3977},{"Age":98,"lx":3069},
            {"Age":99,"lx":2330},{"Age":100,"lx":1739},{"Age":101,"lx":1276},
            {"Age":102,"lx":919},{"Age":103,"lx":649},{"Age":104,"lx":449},
            {"Age":105,"lx":304},{"Age":106,"lx":202},{"Age":107,"lx":131},
            {"Age":108,"lx":83},{"Age":109,"lx":51},{"Age":110,"lx":31}]'''


def annuityCalculator(Data, intRate=.0629, spouseAgeDiff=5, spousalBenefit=.5, Type='SLA'):
    Data = pd.read_json(Data)
    PV = 1/(1+intRate)
    Data = Data[['Age', 'lx']]
    Data['dx'] = Data['lx'] * PV ** Data['Age']

    Data.sort_values(by='Age', ascending=False, inplace=True)
    Data['nx'] = Data['dx'].cumsum()
    Data.sort_values(by='Age', inplace=True)
    Data['SLA'] = (Data['nx'] + Data['nx'].shift(-1, fill_value=0)) / (2 * Data['dx'])

    Data['dxy'] = Data['lx'].shift(spouseAgeDiff) * Data['lx'] * PV ** (Data['Age'] - spouseAgeDiff / 2)

    Data.sort_values(by='Age', ascending=False, inplace=True)
    Data['nxy'] = Data['dxy'].cumsum()
    Data.sort_values(by='Age', inplace=True)

    Data['JL'] = Data['SLA'] + \
                 (Data['nx'].shift(5) + Data['nx'].shift(4)) / (2 * Data['dx'].shift(5)) - \
                 (Data['nxy'] + Data['nxy'].shift(-1)) / (2 * Data['dxy'])
    Data['Cost_of_Pension'] = (Data['SLA'] + Data['JL']) / 2
    Data['Rev_Element'] = Data['JL'] - Data['SLA']
    Data['Spousal_Benefit'] = round(Data['SLA'] + spousalBenefit * Data['Rev_Element'], 4)

    if Type == 'SLA':  # Single Life
        return Data.loc[Data['Age'] == 60, 'SLA'].tolist()[0]
    else:  # With Spousal Benefit Mortality
        return Data.loc[Data['Age'] == 60, 'Spousal_Benefit'].tolist()[0]

def EfficientFrontier():
    mu = Mean()
    sigma = Sigma()

    # Get Scenarios
    Combinations = np.array(np.meshgrid(range(0, 105, 5), range(0, 105, 5), range(0, 105, 10))).T.reshape(-1, 3)

    # take only cases with sum of allocation = 100
    CombinationsFiltered = Combinations[np.sum(Combinations, axis=1) == 100]

    # Calculate Mean & Std Dev
    Output = np.zeros([np.size(CombinationsFiltered, 0), 3])

    for x in range(len(CombinationsFiltered)):
        Allocation = CombinationsFiltered[x]
        Output[x, 0] = np.sum(np.multiply(Allocation, mu))
        Output[x, 1] = (np.dot(Allocation, np.dot(sigma, Allocation.T))) ** .5

    Output[:, 0] = np.round_(Output[:, 0], 1)

    # Calculate Efficient Frontier
    for x in range(len(Output)):
        Output[x, 2] = np.count_nonzero((Output[:, 0] >= Output[x, 0]) * (Output[:, 1] < Output[x, 1])) == 0

    Output = np.hstack((CombinationsFiltered, Output))
    return Output