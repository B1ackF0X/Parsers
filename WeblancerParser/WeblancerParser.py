#!/usr/bin/env python3

import re
import csv
import urllib.request

from clint.textui import progress
from bs4 import BeautifulSoup

BASE_URL = 'http://www.weblancer.net/jobs/'

def turning_date(string):
    template = r'\d{2}.\d{2}.\d{4}'
    
    ddmmyy = re.findall(template, string)

    ddmm = re.findall(r'\d{2}', re.findall(template, string)[0])
    dd = ddmm[0]
    mm = ddmm[1]

    new_string = re.findall(r'\d{4}', ddmmyy[0])[0] + '.' + mm + '.' + dd

    return re.sub(template, new_string, string)


def get_html(url):
	response = urllib.request.urlopen(url)
	return response.read()

def get_page_count(html):
	soup = BeautifulSoup(html)
	paggination = soup.find('ul', class_='pagination')
	
	return int(re.findall(r'[0-9]+', paggination.find_all('a')[-1]['href'])[0])

def parse(html):
	soup = BeautifulSoup(html)
	common_rows = soup.find('div', class_='col-xs-12 page_content col-lg-9')
	
	projects = []
	
	for row in common_rows.find_all('div', 'row'):
		
		projects.append({
			'title' : row.find('div', 'col-sm-7 col-lg-8').find('a').text,
			'categories' : [category.text for category in 
                    row.find('div', 'col-xs-12 text-muted').find_all('a', 'text-muted')],
			'price': row.find('div', 'col-sm-1 amount title').text.strip(),
			'application': row.find('div',
						'col-sm-3 text-right text-nowrap hidden-xs').text.strip(),
			'time ago': row.find('div', 'col-xs-12 text-muted').find('span',
							class_='time_ago').text,
			'date': turning_date(row.find('div', 'col-xs-12 text-muted').find('span',
                            class_='time_ago')["title"])
		})
	
	return projects

def save(projects, path):
	with open(path, 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(('Project', 'Categories', 'Price', 'Application', 'Time Ago', 'Date'))
		
		for project in projects:
			writer.writerow((project['title'], ', '.join(project['categories']), project['price'], project['application'], project['time ago'], project['date']))

def main():
	page_count = get_page_count(get_html(BASE_URL))
	
	print('Всего найдено страниц: %d' % page_count)
	
	projects = []
	
	for page in progress.bar(range(1, page_count+1)):
		projects.extend(parse(get_html(BASE_URL + '?page=%d' % page)))
	
	save(projects, 'projects.csv')

if __name__ == '__main__':
	main()
