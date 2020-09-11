import re
import os
import time
import selenium
import pandas as pd
from selenium import webdriver
from requests_html import HTML
from selenium.webdriver.chrome.options import Options


# Use Selenium without opening the browser
# Might have to disable the headless option if amazon starts askin for captcha
options = Options()
options.add_argument('--headless')
browser = webdriver.Chrome(options = options)

# Create paths for the data files
base_dir = os.path.dirname(os.getcwd())
# os.getcwd() gives the path of the current directory, dirname gives the name of the parent directory (i.e one step above) 
data_dir = os.path.join(base_dir,'Data')
# os.path.join(a,b) creates a path a/b
os.makedirs(data_dir,exist_ok=True)
# os.makedirs creates the directories on the path specified. exist_ok=true means it wont return an error if the directories exists
file_path = os.path.join(data_dir,"urls.csv")

# Read csv files using pandas
urls = pd.read_csv(file_path)



def scrape_data(url):
	# Open the url in the browser(hidden) using selenium
    browser.get(url)
    
    # Timeout between each query to prevent errors and amazon might block account if too fast
    time.sleep(2)

    # Get all the HTML data from the website,i.e inside the <body> tag
    html_data = browser.find_element_by_css_selector('body').get_attribute("innerHTML")
    # Convert the data to usable data. HTML() is imported from requests_html
    html_str = HTML(html=html_data)
    

    avbl = html_str.find("#availability")[0].text
    title_el = html_str.find('#productTitle')[0].text

    #This will contain all the data for the particular item
    data_el = []
    
    if not avbl.startswith("Currently"):
        price_el = html_str.find('#priceblock_ourprice')[0].text
        try:
            saving_el = html_str.find("#regularprice_savings")[0].text.split('(')[1].split(')')[0]
        except:
            saving_el = "0%"

        data_el.append({"Title": title_el, "Price": price_el, "Available":avbl, "Saving": saving_el})
    else:
        avbl = avbl.split('.')[0]
        data_el.append({"Title": title_el, "Price": "NA", "Available":avbl, "Saving": "NA"})
            
    return data_el

# Create url from urls and pass them to the scrape function
def get_data(urls):
    dataset = []
    for url in urls:
    	# Every row of this datasets contain info about one item
        dataset.append(scrape_data(url)[0])
        
    return dataset


# This is the url list that we get from the csv file
urls_list = []
# df.shape returns a tuple (no. of rows,no. of cols)
for i in range(urls.shape[0]):
	# iloc is used to select by index, the ["Urls"] is the column name
    if urls.iloc[i]["Urls"].startswith('http'):
        urls_list.append(urls.iloc[i]["Urls"])

dataset = get_data(urls_list)
#Create a pd dataframe using the collected data
df = pd.DataFrame(dataset)
#Show the data of all the items
df.head(n=urls.shape[0])


# Save the dataframe to a csv file
target_filepath = os.path.join(data_dir,'target.csv')
df.to_csv(target_filepath,index=False)






