import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import unquote

def remove_words(text, word_list):
    for word in word_list:
        text = text.replace(word, '')
    return text

def clip_at_final_word(text, final_word):
    if final_word in text:
        final_idx = text.rfind(final_word)
        print('final_idx:',final_idx)
        return text[:final_idx]
    return text

BASE_WIKI_URL = 'https://namu.wiki/w/'
WORD_LIST = ['[편집]']
FINAL_WORD = '이 저작물은 CC BY-NC-SA 2.0 KR에 따라 이용할 수 있습니다. (단, 라이선스가 명시된 일부 문서 및 삽화 제외)기여하신 문서의 저작권은 각 기여자에게 있으며, 각 기여자는 기여하신 부분의 저작권을 갖습니다.나무위키는 백과사전이 아니며 검증되지 않았거나, 편향적이거나, 잘못된 서술이 있을 수 있습니다.나무위키는 위키위키입니다. 여러분이 직접 문서를 고칠 수 있으며, 다른 사람의 의견을 원할 경우 직접 토론을 발제할 수 있습니다.'
INTERNAL_LINK_START = '/w/'
INTERNAL_LINK_EVIDENCE = [INTERNAL_LINK_START]
EXTERNAL_LINK_EVIDENCE = ['https:/', 'http:/']

class InternalLink:
    def __init__(self, url):
        self.url = url
        encoded_name = url[len(INTERNAL_LINK_START):]
        self.page_name = unquote(encoded_name)

    def __str__(self):
        return self.page_name

    def get_page(self):
        return page(self.page_name)

class Page:
    def __init__(self, name):
        self.name = unquote(name)
        self.page_url = BASE_WIKI_URL+self.name
        res = requests.get(self.page_url)
        self.raw_text = res.text
        self.page_exists = (False if ('해당 문서를 찾을 수 없습니다.' in self.raw_text) else True)
        self.pure_text = None
        self.external_links = None
        self.internal_links = None
        self.category = None
        
    def parse_text(self):
        soup = BeautifulSoup(self.raw_text)
        
        soup_text = soup.text
        soup_text = remove_words(soup_text, WORD_LIST)
        final_text = clip_at_final_word(soup_text, FINAL_WORD)
        self.pure_text = final_text

        link_list = []
        for link in BeautifulSoup(self.raw_text, parse_only=SoupStrainer('a')):
            if link.has_attr('href'):
                link_list.append(link['href'])

        self.internal_links = []
        self.external_links = []
        for link_url in link_list:
            if any(evidence in link_url for evidence in EXTERNAL_LINK_EVIDENCE):
                self.external_links.append(link_url)
            elif any(evidence in link_url for evidence in INTERNAL_LINK_EVIDENCE):
                self.internal_links.append(InternalLink(link_url))

    def get_pure_text(self):
        if self.pure_text is None:
            self.parse_text()
        return self.pure_text

    def get_internal_links(self):
        if self.internal_links is None:
            self.parse_text()
        return self.internal_links

    def get_external_links(self):
        if self.external_links is None:
            self.parse_text()
        return self.external_links

    def __str__(self):
        return self.name

class Category(Page):
    def __init__(self, url):
        super(url)
        self.member_pages = []
