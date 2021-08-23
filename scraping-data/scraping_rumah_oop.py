from bs4 import BeautifulSoup
import pandas as pd
import requests
import cloudscraper
import csv
import os.path
import time

class ScrapeRumah:
	def __init__(self, path):
		self.path = path
		self.count = 1

	def start(self):
		for page in range(1, 1000):
			meta_data = self.request_data(page)
			data_parse = self.parsing_data(meta_data)
			save_data = self.save_to(data_parse)
			time.sleep(10)

	def request_data(self, page):
		url = f"https://www.rumah.com/properti-dijual/{page}?district_code=IDJK03&property_type=B&property_type_code^%^5B0^%^5D=BUNG&region_code=IDJK"
		scraper = cloudscraper.create_scraper()
		result = scraper.get(url).text
		return result

	def parsing_data(self, content):
		soup = BeautifulSoup(content, 'lxml')
		first = soup.find('div', class_="listing-widget-new small-listing-card")
		datas = first.find_all('div', class_="col-xs-12 col-sm-7 listing-description")
		my_dict = {'nama_rumah': [], 'kamar_mandi': [], 'kamar_tidur': [], 'luas_m2': [], 'harga': [], 'harga_m2': [], 'alamat': [], 'link': []}
		for data in datas:
			nama_rumah = data.a.text
			alamat = data.span.text
			link = data.h3.a['href']
			harga_raw = data.find('span', class_="price").text.lower().split(' ')
			harga = self.benerin_harga(harga_raw)
			raw = data.find_all('li', class_="listing-floorarea pull-left")
			luas_m2 = 0
			harga_m2 = 0
			if(len(raw)==2):
				luas_m2 = raw[0].text.split()[-2]
				harga_m2 = raw[1].text.split()[1].replace('.', '')

			kamar_mandi = data.find('span', class_="bath")
			kamar_tidur = data.find('span', class_='bed')
			if(kamar_mandi == None):
				kamar_mandi = None
			else:
				kamar_mandi = kamar_mandi.text

			if(kamar_tidur == None):
				kamar_tidur = None
			else:
				kamar_tidur = kamar_tidur.text
			print(f"{self.count} {nama_rumah}\n{alamat}\n{harga}\n{harga_m2}\n")
			my_dict['nama_rumah'].append(nama_rumah)
			my_dict['kamar_mandi'].append(kamar_mandi)
			my_dict['kamar_tidur'].append(kamar_tidur)
			my_dict['luas_m2'].append(luas_m2)
			my_dict['harga'].append(harga)
			my_dict['harga_m2'].append(harga_m2)
			my_dict['alamat'].append(alamat)
			my_dict['link'].append(link)
			self.count+=1
		return my_dict

	def convert_0(self, harga, jumlah_0):
		if(',' in harga[0]):
			harga_split = harga[0].split(',')
			harga_replace = harga[0].replace(',', '')
			berapa_0 = jumlah_0-len(harga_split[1])
			berapa_0 = berapa_0*"0"
			result = harga_replace+berapa_0
		else:
			berapa_0 = jumlah_0*"0"
			result = harga[0]+berapa_0
		return result

	def benerin_harga(self, harga):
		print(len(harga))
		if(len(harga) == 2):
			besaran_harga = harga[1]
			if(besaran_harga == 'm'):
				result = self.convert_0(harga, jumlah_0=9)
				return result
			elif(besaran_harga == 'jt'):
				result = self.convert_0(harga, jumlah_0=6)
				return result
		else:
			return 0

	def save_to(self, dict_row):
		path_output = self.path+"data_harga_rumah2.csv"
		is_new = not os.path.isfile(path_output)
		rows = zip(*dict_row.values())
		modes = 'a'
		if is_new:
		    os.makedirs(os.path.dirname(path_output), exist_ok=True)
		    modes = 'w'
		with open(path_output, mode=modes, newline='', encoding='utf-8') as csv_file:
		    writer = csv.writer(csv_file)
		    if is_new:
		        writer.writerow(dict_row.keys())
		    for row in rows:
		        writer.writerow(row)

path_output = '/content/data/'
scraping = ScrapeRumah(path_output)
scraping.start()