# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 18:01:09 2022

@author: Fernando
"""

#%%
#S Rank
import pandas as pd
import numpy as np
import requests


url='https://www.fundamentus.com.br/fii_resultado.php'
header = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"  
 }
r = requests.get(url, headers=header)

realestate=pd.read_html(r.text, decimal=',',thousands='.')[0]

print(realestate)

#%%
realestate=realestate[['Papel','Segmento','Cotação','Dividend Yield','P/VP','Liquidez']]
realestate=realestate.rename(columns={'Papel':'Ticker','Segmento':'Subsector','Cotação':'Price','P/VP':'P/B','Liquidez':'Liquidity'})
#Filter 1
realestate=realestate[realestate['Liquidity']>200000]
realestate=realestate.set_index('Ticker')

#%%
realestate['Div_mean']=' '
realestate['Div_median']=' '
realestate['Mandate']=' '
for i in (list(realestate.index)):
  url1='https://statusinvest.com.br/fundos-imobiliarios/'+str.lower(i)
  r1 = requests.get(url1, headers=header)
  url2='https://www.fundamentus.com.br/detalhes.php?papel='+str(i)
  r2=requests.get(url2, headers=header)
  try:
    dividend=pd.read_html(r1.text, decimal=',',thousands='.')[0]
    realestate.loc[i,'Div_mean']=dividend['Valor'].mean()
    realestate.loc[i,'Div_median']=dividend['Valor'].median()
    mandate=pd.read_html(r2.text)[0]
    realestate.loc[i,'Mandate']=mandate.iloc[2,1]
  except:
    pass

#%%
realestate['Div_mean']=realestate['Div_mean'].replace(' ',np.nan)
realestate['Div_median']=realestate['Div_median'].replace(' ',np.nan)
realestate['Dividend Yield']=realestate['Dividend Yield'].str.replace(',','.')
realestate['Dividend Yield']=realestate['Dividend Yield'].str.rstrip('%').astype(float)/100

realestate[['Div_mean','Div_median']]=realestate[['Div_mean','Div_median']].astype(float)

realestate['|Mean-Median|']=100*abs(realestate['Div_mean']-realestate['Div_median'])/realestate['Price']

print(realestate.info())
#%%
#Filter 2: Mandate
realestate=realestate[realestate['Mandate']!='Desenvolvimento para Renda']

#Filter3: |Mean-Median|
realestate=realestate[realestate['|Mean-Median|']<0.1]

realestate=realestate.sort_values(by='Dividend Yield',ascending=False)
realestate['rank_div']=range(1,len(realestate)+1)
realestate=realestate.sort_values(by='P/B')
realestate['rank_P/B']=range(1,len(realestate)+1)

realestate['ranking']=realestate['rank_div']+realestate['rank_P/B']

ranking=realestate['ranking'].sort_values()

print('The best 15 tickers are: ')
print(ranking.iloc[0:15])


















