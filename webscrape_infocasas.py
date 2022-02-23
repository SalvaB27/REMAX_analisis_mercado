# I made this algorithm on the run, it could be refined but it gets the job done.

import sys

import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
from urllib.request import Request, urlopen

base_url = 'https://www.infocasas.com.uy/alquiler/apartamentos/montevideo/ciudad-vieja'

data = []
imgs ={} 

req = Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()
soup = BeautifulSoup(webpage, 'html.parser')

total_pages = int(soup.find('ul').contents[-2].text)

for i in range(0, total_pages):
    try: 
        if i != 0:
            url = base_url + '/pagina' + str(i + 1)

            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = BeautifulSoup(webpage, 'html.parser')

            print('Page ' + str(i))
        
        container = soup.div.div.find('div', {'class': 'ant-row-top'})
        content = container.contents
    except AttributeError:
        print('AttributeError -> page: ' + str(i))
        continue
    else:
        for x in range(0,len(content)):
            print('Number -> ' + str(x))
            tries = 0
            while(tries<3):
                try:
                    tries += 1
                    href = content[x].find('a', {'class': 'containerLink'})['href']
                    url_2 = 'https://www.infocasas.com.uy' + href
                    
                    req_2 = Request(url_2, headers={'User-Agent': 'Mozilla/5.0'})
                    webpage_2 = urlopen(req_2).read()
                    intra_soup = BeautifulSoup(webpage_2, 'html.parser')

                    list = {}

                    list['Name'] = intra_soup.find('h1').text
                    list['Price'] = intra_soup.find('strong').text

                    technical_sheet = intra_soup.find('div', {'class':'technical-sheet'})
                    for y in range(0, len(technical_sheet.contents)):
                        col = technical_sheet.contents[y].find_all('span', {'class': 'ant-typography'})[1].text
                        val = technical_sheet.contents[y].find('strong').text
                        list[col] = val
                
                    description = intra_soup.find_all('div', {'class': 'description-container'})[0].find('h4').text
                    if bool(intra_soup.find_all('div', {'class': 'description-container'})[0].p) == True:
                        paragraph = intra_soup.find_all('div', {'class': 'description-container'})[0].p.text
                    else:
                        paragraph = intra_soup.find_all('div', {'class': 'description-container'})[0].span.text

                    list[description] = paragraph

                    data.append(list)
                    imgs[x] = intra_soup.find_all('img')
                except AttributeError:
                    print('retrying....(page:' + str(i) + ' number:' + str(x) + ')')
                except IndexError:
                    print('Index Error -> (page:' + str(i) + ' number:' + str(x) + ')')
                else:
                    break
                    
len(soup.div.div.find('div', {'class': 'ant-row-top'}).contents)
df = pd.DataFrame(data)

# Data ready for cleaning and wrangling.
df.to_excel('apalq.xlsx')
