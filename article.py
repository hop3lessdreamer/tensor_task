import requests
import re
import bs4
import os
import config


class Article:
	def __init__(self, url: str):
		self.url = url
		try:
			page = requests.get(url)
		except requests.exceptions.ConnectionError:
			raise 'Не удается получить доступ к странице. Проверьте URL!'
		self.soup = bs4.BeautifulSoup(page.text, 'html.parser')
		self.remove_div_class_footer(config.EXCLUDED_DIV_CLASS_NAME)
		self.remove_tag(config.EXCLUDED_TAGS)
		self.get_article_title_tags()
		self.get_article_tags()
		self.article_title = self.edit_article_text(self.article_title_tags, config.STRING_LENGTH)
		self.article_text = self.edit_article_text(self.article_text_tags, config.STRING_LENGTH)
		self.generate_path_to_article()
		self.write_data_to_file(self.article_title + self.article_text)

	def remove_div_class_footer(self, class_names: list):
		for class_name in class_names:
			try:
				for tag in self.soup.find_all('div', {'class': re.compile(class_name)}):
					tag.extract()
			except AttributeError:
				pass

	def remove_tag(self, tags: list):
		for tag in tags:
			try:
				self.soup.find(tag).extract()
			except Exception:
				pass

	def get_article_title_tags(self):
		self.article_title_tags = self.soup.find_all('h1')

	def get_article_tags(self):
		self.article_text_tags = self.soup.find_all('p')

	def edit_article_text(self, text: bs4.element.ResultSet, string_len: int) -> str:
		self.article_text = ''
		for data in text:
			links = data.find_all('a')
			if links != '':
				for link in links:
					data.a.replace_with(link.text + ' [' + link['href'] + '] ')
			data = data.text.replace('\n', '').lstrip()
			self.symbols_count = 0
			for word in data.split(' '):
				if 'http' in word:
					for url in word.split('-'):
						article_text = self.make_string_width(url, string_len, word, '-')
				else:
					article_text = self.make_string_width(word, string_len, data, ' ')
			self.article_text += '\n\n'
		return self.article_text

	def make_string_width(self, word: str, string_len: int, data: list, split: str):
		self.symbols_count += len(word)
		if self.symbols_count + 1 > string_len:
			self.article_text = self.article_text.rstrip()
			self.article_text += '\n'
			self.symbols_count = len(word)
		if word != data.split(split)[-1]:
			self.article_text += word + split
		else:
			self.article_text += word
		self.symbols_count += 1

	def generate_path_to_article(self):
		splited_url = self.url.split('/')
		splited_url = list(filter(bool, splited_url))
		self.path = '\\'.join(splited_url[1:-1])
		self.cur_dir = os.getcwd()
		self.file_name = splited_url[-1]
		if '.' in self.file_name:
			self.file_name = self.file_name.split('.')[0]
		self.file_name += '.txt'
		if not os.path.exists(self.path):
			os.makedirs(self.path)
		self.path = '\\' + self.path + '\\'

	def write_data_to_file(self, data: str):
		invalid_symbols = ['/', '\\', '?', '!', ':', '*', '"', '<', '>', '|']
		for symbol in invalid_symbols:
			if symbol in self.file_name:
				self.file_name = self.file_name.replace(symbol, '')
		full_path = self.cur_dir + self.path + self.file_name
		with open(full_path, 'w', encoding='utf8') as file:
			file.write(data)
