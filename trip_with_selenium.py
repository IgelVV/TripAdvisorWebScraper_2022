import json
import re
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL = 'https://www.tripadvisor.com/Tourism-g186591-Ireland-Vacations.html'

# useragent = UserAgent()
useragent = (
    'Mozilla/5.0 (X11; Linux x86_64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/90.0.4430.72 Safari/537.36'
)


class TripAdvisorParser:
    categories = {}
    hotels_data = {}

    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def parse(self, search_categories=('hotels', 'restaurants')):
        for category in search_categories:
            self.categories[category] = None

        self.get_links_to_site_categories()
        self.parse_all_hotels()
        self.parse_all_restaurants()
        # etc

    def get_links_to_site_categories(self) -> None:
        self.driver.get(self.url)
        found_categories = self.driver.find_elements(By.CLASS_NAME, "XUWut")
        for category in self.categories.keys():
            for element in found_categories:
                element_name = element.find_element(By.CLASS_NAME, "biGQs")
                if element_name.text.lower() == category:
                    self.categories[category] = element.get_attribute("href")
                    break
        print(self.categories, '\n')

    def parse_all_hotels(self, filename='hotels.csv') -> None:
        all_hotel_links = self.get_all_hotels_links()
        for hotel_link in all_hotel_links:
            hotel_info = self.parse_hotel_page(hotel_link)
            print(
                hotel_info.name + "\n",
                hotel_info.address + "\n",
                hotel_info.home_page + "\n",
                hotel_info.email + "\n",
                hotel_info.main_image_link + "\n",
                '______________________________________'
            )
            # self.write_to_csv(hotel_info)
            time.sleep(2)

    def get_all_hotels_links(self) -> list:
        all_hotel_links = []
        self.driver.get(self.categories['hotels'])
        all_hotel_links.extend(self.get_hotels_from_page())
        while len(all_hotel_links) < 60:  # just 120 for tests
            self.click_next_button()
            time.sleep(5)
            all_hotel_links.extend(self.get_hotels_from_page())
            print(len(all_hotel_links))

        return all_hotel_links

    def get_hotels_from_page(self) -> list:
        hotel_links = []
        hotels_buttons = self.driver.find_elements(By.CLASS_NAME, "property_title")
        for element in hotels_buttons:
            hotel_links.append(element.get_attribute("href"))
        return hotel_links

    def click_next_button(self) -> None:
        # self.driver.execute_script('window.scrollBy(0,7000)', '')
        try:
            see_all_button = self.driver.find_element(By.CLASS_NAME, "pexOo")
            see_all_button.click()
        except NoSuchElementException:
            pass

        next_buttons = self.driver.find_elements(By.CLASS_NAME, "next")
        next_buttons[1].click()

    def parse_hotel_page(self, link):
        hotel_info = Hotel()
        self.driver.get(link)
        time.sleep(1)
        hotel_info.name = self.parse_hotel_name()
        hotel_info.email = self.parse_hotel_email()
        hotel_info.address = self.parse_hotel_address()
        hotel_info.home_page = self.parse_hotel_home_page()
        hotel_info.main_image_link = self.parse_hotel_main_image_link()

        return hotel_info

    def parse_hotel_name(self) -> str:
        hotel_name = self.driver.find_element(By.CLASS_NAME, 'QdLfr').text
        return hotel_name

    def parse_hotel_email(self) -> str:
        html_data = self.driver.page_source
        data = re.search(r'window\.__WEB_CONTEXT__=(\{.*?});', html_data).group(1)
        data = json.loads(data.replace('pageManifest', '"pageManifest"'))
        return self.get_emails_from_data(data)

    def get_emails_from_data(self, data):
        email = ''
        for email_parts in self.get_all_email_parts(data):  # only the first found email address
            for part in email_parts:
                email += part
            return email
        else:
            return 'email not found'

    # can find all emails on a page
    def get_all_email_parts(self, val):
        if isinstance(val, dict):
            for k, v in val.items():
                if k == "emailParts":
                    if v:
                        yield v
                else:
                    yield from self.get_all_email_parts(v)
        elif isinstance(val, list):
            for v in val:
                yield from self.get_all_email_parts(v)
        elif isinstance(val, str) and val.startswith('{"'):
            val = json.loads(val)
            yield from self.get_all_email_parts(val)

    def parse_hotel_address(self) -> str:
        hotel_address = self.driver.find_element(By.CLASS_NAME, 'fHvkI').text
        return hotel_address

    def parse_hotel_home_page(self) -> str:
        try:
            hotel_home_page = self.driver.find_element(By.CLASS_NAME, 'YnKZo').get_attribute("href")
        except NoSuchElementException:
            hotel_home_page = 'no website'
        return hotel_home_page

    def parse_hotel_main_image_link(self) -> str:
        hotel_main_image_link = self.driver.find_element(
            By.XPATH,
            "//div[contains(@class,'zVGHf')]/picture/source[last()]"
        ).get_attribute("srcset").split(',')[-1].split(' ')[0]
        return hotel_main_image_link

    def parse_all_restaurants(self):
        ...


class Hotel:

    def __init__(self, name='', home_page='', address='', email='', main_image_link=''):
        self.category = 'hotel'
        self.name = name
        self.home_page = home_page
        self.address = address
        self.email = email
        self.main_image_link = main_image_link

    def to_csv(self):
        ...


def main():
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={useragent}')
    driver = webdriver.Chrome(executable_path=r'chromedriver', options=options)

    try:
        parser = TripAdvisorParser(driver, URL)
        parser.parse()
        # driver.maximize_window()
    except Exception as e:
        raise e
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()
