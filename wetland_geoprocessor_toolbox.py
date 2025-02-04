#   Created by: Cleve Davis
#   Created date: January 5, 2023
#
#
####
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import arcpy
import math
# User Inputs:
cfs = float(arcpy.GetParameterAsText(0))
#cfs = 400
# Surface area (sa) must be in meters squared and calculated from a polygon the user makes in IrrigationViz. Example below is based upon acres.
acres = float(arcpy.GetParameterAsText(1))
#acres = 50
sa = 4046.86 * acres
# Period of time to evaluate
days = float(arcpy.GetParameterAsText(2))
#days = 180
# Advance option
no3_data = float(arcpy.GetParameterAsText(3))
po4_data = float(arcpy.GetParameterAsText(4))
#no3_data = 5
#po4_data = 0.5
# Logic to calculate load reduction based upon user input
load_risk = arcpy.GetParameterAsText(5)
#load_risk = "low" #input("Enter the load level category (i.e., low, mid, or high of nitrate and phosphorus) of fertilizer pollution: ")
#no3_data = input("Enter the average load of nitrate in ppm or mg/L: ")
#po4_data = input("Enter the avearge load of orthophospate in ppm or mg/L: ")
# Nitrate and Orthophosphate logic
if load_risk == "low":
    ppm_no3 = np.array([0.12, 2.2])
    ppm_po4 = np.array([0.01, 0.075])
elif load_risk == "mid":
    ppm_no3 = np.array([2.21, 5.0])
    ppm_po4 = np.array([0.076, 0.1])
elif load_risk == "high":
    ppm_no3 = np.array([5.01, 10])
    ppm_po4 = np.array([0.11, 1])
else:
    ppm_no3 = no3_data
    ppm_po4 = po4_data
'''To estimate removal of nitrate and phosphate this function does the following: cfs to m3/day, various conversions between units, volume of the 
wetland, and hydraulic residence time in days. Wetland depth assumes the following (from 2007 USDA TN Biology No.22 - revised): 
sediment basin 9'(3%), primary grass 2'(23%), vegetated wetland 1'(23%), deep water pond 8'(41%), and polish filter 2' (10%). 
The function also calculates mass fertilzer waste entering constructed wetland in kg/yr and relies upon the removal rate constants (k) 
for nitrate and phosphate by (Cheng and Basu 2017 pg. 5049).'''
def removed_kg_time():
    flow_m3_day = cfs * 60 * 60 * 24 * 0.0283168
    d_ft = 9*0.03 + 2*0.23 + 1*0.23 + 8*0.41 + 2*.10
    d = d_ft*0.3048
    vol = d*sa
    t = vol/flow_m3_day
    kno3 = 0.635 * t ** -0.75
    kpo4 = 0.306 * t ** -0.65
    M_input_no3 = flow_m3_day * days * ppm_no3 * 1000 * .000001
    M_input_po4 = flow_m3_day * days * ppm_po4 * 1000 * .000001
    p_wet_i_no3 = (1 - np.exp(-kno3*t))*100
    p_wet_i_po4 = (1 - np.exp(-kpo4*t))*100
    return np.round_(M_input_no3*(p_wet_i_no3/100), 2), np.round_(M_input_po4*(p_wet_i_po4/100), 2)
#print('Over '+ str(days)+ ' days,' + str(removed_kg_time()) + 'kgs of nitrate and orthophosate was potentially removed from a ' + str(acres) + ' acre construced surface flow wetland with an average cfs of ' + str(cfs))
def percent_removed_time():
    flow_m3_day = cfs * 60 * 60 * 24 * 0.0283168
    d_ft = 9*0.03 + 2*0.23 + 1*0.23 + 8*0.41 + 2*.10
    d = d_ft*0.3048
    vol = d*sa
    t = vol/flow_m3_day
    kno3 = 0.635 * t ** -0.75
    kpo4 = 0.306 * t ** -0.65
    M_input_no3 = flow_m3_day * days * ppm_no3 * 1000 * .000001
    M_input_po4 = flow_m3_day * days * ppm_po4 * 1000 * .000001
    p_wet_i_no3 = (1 - np.exp(-kno3*t))*100
    p_wet_i_po4 = (1 - np.exp(-kpo4*t))*100
    return np.round_(p_wet_i_no3/100, 2), np.round_(p_wet_i_po4/100, 2)
#print('Over '+ str(days)+ ' days,' + str(percent_removed_time(sa)) + 'percent of nitrate and orthophosate was potentially removed a ' + str(acres) +  ' acre construced surface flow wetland with an average cfs of ' + str(cfs))
# load in ppm retained (R) as result of installing constructed wetland after given time
def ppm_remaining_time():
    flow_m3_day = cfs * 60 * 60 * 24 * 0.0283168
    d_ft = 9*0.03 + 2*0.23 + 1*0.23 + 8*0.41 + 2*.10
    d = d_ft*0.3048
    vol = d*sa
    t = vol/flow_m3_day
    kno3 = 0.635 * t ** -0.75
    kpo4 = 0.306 * t ** -0.65
    M_input_no3 = flow_m3_day * days * ppm_no3 * 1000 * .000001
    M_input_po4 = flow_m3_day * days * ppm_po4 * 1000 * .000001
    p_wet_i_no3 = (1 - np.exp(-kno3*t))*100
    p_wet_i_po4 = (1 - np.exp(-kpo4*t))*100
    no3_reduction = M_input_no3*(p_wet_i_no3/100)
    po4_reduction = M_input_po4*(p_wet_i_po4/100)
    acre = sa * 0.0002471053815
    return np.round_((ppm_no3 * (M_input_no3 - no3_reduction)/M_input_no3), 2), np.round_((ppm_po4 * (M_input_po4 - po4_reduction)/M_input_po4), 2)
#print('Estimated outflow load of nitrate and orthophosphate in mg/L(ppm) exiting the wetland was ' + str(ppm_remaining_time(sa)))
'''
***Empirical method to estimate first year construction cost of installing a constructed wetland. 
To account for inflation, the "All items in U.S. city average, all urban consumers, seasonally 
adjusted (Month of June)" CPI index was used. Future update should subset data from CPI for all Urban Consumers. 
'''
pdata1 = [['BMP', 30000, 65000, 47500, 1999, 166.00, 257.214],
          ['Tyndall & Bowman', np.nan, np.nan, 10022, 2016, 240.144, 257.214],
          ['Noack', np.nan, np.nan, 33837, 2018, 251.176, 257.214],
          ['OSU', np.nan, np.nan, 10000, 2016, 240.144, 257.214],
          ['Newton', 22000, 87000, 54500, 2006, 201.8, 257.214], ]
df1 = pd.DataFrame(pdata1, columns=['Source', 'LowerEstimate', 'UpperEstimate', 'MidPoint',
                                    'EstimateYear', 'CPIEY', 'CurrentCPI'])
inflation = (df1["CurrentCPI"]-df1["CPIEY"])/df1["CPIEY"]
dollars2020 = inflation*df1["MidPoint"]
cw_cost = dollars2020+df1["MidPoint"]
# This function calculates total cost for installing a constructed wetland
def total_cost():
    mu = np.mean(cw_cost)
    sigma = np.std(cw_cost)
    n = cw_cost.shape[0]-1
    t = 2.776
    ci_up = mu+(t*sigma/math.sqrt(n))
    ci_dw = mu-(t*sigma/math.sqrt(n))
    acre = sa * 0.0002471053815
    return np.round_(acre*ci_dw, 2), np.round_(acre*mu, 2), np.round_(acre*ci_up, 2)
#print('Total estimated (i.e., lower CI, mean, upper CI) construction cost: ' + str(total_cost(sa)))
# This function calculates total cost per acre for installing a constructed wetland
def cost_acre():
    mu = np.mean(cw_cost)
    sigma = np.std(cw_cost)
    n = cw_cost.shape[0]-1
    t = 2.776
    ci_up = mu+(t*sigma/math.sqrt(n))
    ci_dw = mu-(t*sigma/math.sqrt(n))
    return np.round_(ci_dw, 2), np.round_(mu, 2), np.round_(ci_up, 2)
######INPUTS FOR LOAD RISK#####
input_no3=str(ppm_no3)
input_po4=str(ppm_po4)            
arcpy.SetParameter(6,str(input_no3[0:100])) 
arcpy.AddMessage(ppm_no3)
arcpy.SetParameter(7,str(input_po4[0:100])) 
arcpy.AddMessage(ppm_po4)
####OUTPUTS######
#Kilograms removed
kg_removed = str(removed_kg_time()) #2 results
print(kg_removed)
arcpy.SetParameter(8,str(kg_removed[0:100])) 
arcpy.AddMessage(kg_removed[0:100])
#Percent removed 
pct_removed = str(percent_removed_time()) #2 results
print(pct_removed)
arcpy.SetParameter(9,str(pct_removed[0:100])) 
arcpy.AddMessage(pct_removed[0:100])
#Remaining load
load = str(ppm_remaining_time()) #2 results
print(load)
arcpy.SetParameter(10,str(load[0:100])) 
arcpy.AddMessage(load[0:100])
#Total estimated cost to construct wetland
t_cost=str(total_cost())
print(t_cost)
arcpy.SetParameter(11,str(t_cost[0:100])) 
arcpy.AddMessage(t_cost[0:100])
#Estimated cost per acre to install constructed wetland
c_acre=str(cost_acre())
print(c_acre)
arcpy.SetParameter(12,str(c_acre[0:100])) 
arcpy.AddMessage(c_acre[0:100])
