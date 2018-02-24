from bs4 import BeautifulSoup
import requests
import pandas as pd


class Scraper(object):

    '''docstring'''

    list_count = 0
    page_num = 1
    t = '&t=0'
    s = '&s=' + str(list_count)
    r = '&r=20'
    p = '&p=' + str(page_num)
    o = '&o=listingdate-desc'

    def set_web_site(self, web_site):

        '''docstring'''

        self.web_site = web_site
        self.search_term = web_site.split('/')[-2][1:]
        self.start_url = (
            'https://www.century21.com/propsearch-async?lid=' +
            self.search_term)
        self.main_url = (self.start_url + Scraper.t + Scraper.s + Scraper.r +
                         Scraper.p + Scraper.o)

        return web_site, self.search_term, self.start_url, self.main_url

    def url_list(self):

        '''docstring'''

        self.r = requests.get(self.main_url)
        self.c = self.r.content
        self.soup = BeautifulSoup(self.c, 'html.parser')

        try:
            self.num_listings = (
                int(self.soup.find('div', {'class': 'results-label'})
                    .text.replace('(', '').replace(')', '')
                    .split()[-1].replace(',', ''))
                )
        except(AttributeError, TypeError):
            print("\n#### Unable to access site. Is it down? "
                  "Is the URL correct? ####")
            raise

        try:
            url_list = []
            while self.num_listings > 0:

                Scraper.t = '&t=0'
                Scraper.s = '&s=' + str(self.list_count)
                Scraper.r = '&r=20'
                Scraper.p = '&p=' + str(self.page_num)
                Scraper.o = '&o=listingdate-desc'
                page_url = (self.start_url + Scraper.t + Scraper.s + Scraper.r +
                            Scraper.p + Scraper.o)
                url_list.append(page_url)

                self.list_count += 20
                self.num_listings -= 20

            return url_list
        except AttributeError:
            print("\n#### Unable to access site. Is it down? "
                  "Is the URL correct? ####")
            raise



if __name__ == '__main__':
    url = Scraper()
    url.set_web_site(
        'https://www.century21.com/real-estate/ogle-county-il/LNILOGLE/'
    )

    full_url = url.web_site
    list_label = url.web_site.split('/')[-2]
    county = url.web_site.split('/')[-3].split('-')[0]
    state = url.web_site.split('/')[-3].split('-')[-1]
    locale = (f'{county} county, {state}')
    print('\nProcessing List {} County, {}\n'
              .format(str.title(county), str.upper(state)))

    urls = url.url_list()
    full_list = []
    for url in urls:
        r = requests.get(url)
        c = r.content
        soup = BeautifulSoup(c, 'html.parser')
        all = soup.find_all('div', {'class': 'property-card-primary-info'})

        my_list = []
        for item in all:
            my_dict = {}
            try:
                my_dict['Price'] = (
                    item.find('a', {'class': 'listing-price'})
                    .text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['Address'] = (
                    item.find('div', {'class': 'property-address'})
                    .text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['City'] = (
                    item.find('div', {'class': 'property-city'})
                    .text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['Beds'] = (
                    item.find('div', {'class': 'property-beds'}).find('strong')
                    .text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['Baths'] = (
                    item.find('div', {'class': 'property-baths'})
                    .find('strong').text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['Half-Baths'] = (
                    item.find('div', {'class': 'property-half-baths'})
                    .find('strong').text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            try:
                my_dict['Size'] = (
                    item.find('div', {'class': 'property-sqft'})
                    .find('strong').text.replace('\n', '').strip()
                    )
            except AttributeError:
                None
            my_list.append(my_dict)
            full_list.append(my_dict)

    df = pd.DataFrame(full_list)
    list_count = len(df.index)
    print(f'Property Count: {list_count}\n')
    print(f'Outputting results from {full_url} to CSV.\n')
    df.to_csv(f'century21_property_listings_for_{county}_{state}.csv',
              index=False)
