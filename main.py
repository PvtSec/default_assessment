from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
import csv

DOMAIN = "https://clutch.co:443"
SEARCH_URL = f"{DOMAIN}/homepage/search"
headers = {"Content-Type": "application/x-www-form-urlencoded"}
keywords = ['javascript', 'java', 'android', 'cloud', 'developer']
urls = []
fields = ["Company", "Website", "Location", "Contact", "Rating", "Review Count", "Hourly Rate", "Min Project Size", "Employee Size"]


for keyword in keywords:
  payload = {"services": keyword}
  search_response = requests.post(SEARCH_URL, headers=headers, data=payload)
  soup = BeautifulSoup(search_response.text)
  options = soup.find_all('input')
  for x in options:
    url = f"{DOMAIN}/{x['data-url']}"
    if 'packages' not in url:
      urls.append(url)

urls = list(set(urls))


final_data = []
names = []
for url in tqdm(urls):
  url_response = requests.get(url)
  soup = BeautifulSoup(url_response.text)
  last_page = int(soup.find('li', {'class' : 'page-item last'}).a['data-page'])
  
  for page in range(last_page + 1):
    paged_url = f'{url}?page={page}'

    url_response = requests.get(paged_url)
    soup = BeautifulSoup(url_response.text)
    
    companies = soup.find_all('li', {"class": "provider provider-row sponsor"})
    scraped = {}

    for data in companies:
      company_name = data.find('h3', {"class": "company_info"}).text
      company_name = company_name.replace('  ', '').replace('\n', '')

      company_website = data.find('a', {"class": "website-link__item"})['href']
      company_website = company_website.split('//')
      company_website = company_website[0] + '//' + company_website[1].split('/')[0]

      company_location = data.find('span', {"class": "locality"}).text

      company_profile_url = DOMAIN + data.find('a', {"class": "directory_profile"})['href']
      company_profile = requests.get(company_profile_url)
      company_profile_soup = BeautifulSoup(company_profile.text)

      company_contact = company_profile_soup.find('a', {"class" : "contact phone_icon"})
      if company_contact == None:
        company_contact = 'Unavailable'
      else:
        company_contact = company_contact['href'].replace('tel:', '')
        company_contact = requests.utils.unquote(company_contact)

      company_rating = data.find('span', {"class": "rating sg-rating__number"})
      if company_rating == None:
        company_rating = '0'
      else:
        company_rating = company_rating.text
        company_rating = company_rating.replace('  ', '').replace('\n', '')

      company_reviews = data.find('a', {"class": "reviews-link sg-rating__reviews directory_profile"})
      if company_reviews == None:
        company_reviews = '0'
      else:
        company_reviews = company_reviews.text
        company_reviews = company_reviews.replace('  ', '').replace('\n', '').replace(' reviews', '')

      company_hourly_rate = data.find('div', {"data-content": "<i>Avg. hourly rate</i>"}).span.text

      company_proj_size = data.find('div', {"data-content": "<i>Min. project size</i>"}).span.text

      company_employees = data.find('div', {"data-content": "<i>Employees</i>"}).span.text

      scraped["Company"] = company_name
      scraped["Website"] = company_website
      scraped["Location"] = company_location
      scraped["Contact"] = company_contact
      scraped["Rating"] = company_rating
      scraped["Review Count"] = company_reviews
      scraped["Hourly Rate"] = company_hourly_rate
      scraped["Min Project Size"] = company_proj_size
      scraped["Employee Size"] = company_employees
      final_data.append(scraped)
final_data = [dict(t) for t in {tuple(d.items()) for d in final_data}]

with open('Clutch.csv', 'w') as company_csv:
  writer = csv.DictWriter(company_csv, fieldnames=fields)
  writer.writeheader()
  writer.writerows(final_data)