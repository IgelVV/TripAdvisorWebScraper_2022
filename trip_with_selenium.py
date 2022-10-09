import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# URL = 'https://www.tripadvisor.com/Hotels-g186591-Ireland-Hotels.html'
URL = 'https://www.tripadvisor.com/Tourism-g186591-Ireland-Vacations.html'
# URL = 'https://n5m.ru/usagent.html'

# useragent = UserAgent()
useragent = (
    'Mozilla/5.0 (X11; Linux x86_64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/90.0.4430.72 Safari/537.36'
)


class TripAdvisorParser:

    categories = {}

    hotel_links = []
    hotels_data = {}

    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def parse(self, search_categories=('hotels', 'restaurants')):
        for category in search_categories:
            self.categories[category] = None

        self.get_links_to_site_categories()
        self.get_all_hotels()
        self.get_all_restaurants()
        # etc

    def get_links_to_site_categories(self):
        self.driver.get(self.url)
        found_categories = self.driver.find_elements(By.CLASS_NAME, "XUWut")
        for category in self.categories.keys():
            for element in found_categories:
                element_name = element.find_element(By.CLASS_NAME, "biGQs")
                if element_name.text.lower() == category:
                    self.categories[category] = element.get_attribute("href")
                    break
        print(self.categories, '\n')

    def get_all_hotels(self):
        self.driver.get(self.categories['hotels'])
        self.get_hotels_from_page()
        while len(self.hotel_links) < 120:
            self.click_next_button()
            self.get_hotels_from_page()
            time.sleep(3)

    def get_hotels_from_page(self):
        hotels_buttons = self.driver.find_elements(By.CLASS_NAME, "property_title")
        for element in hotels_buttons:
            self.hotel_links.append(element.get_attribute("href"))
        print(len(self.hotel_links))

    def click_next_button(self):
        # self.driver.execute_script('window.scrollBy(0,7000)', '')
        try:
            see_all_button = self.driver.find_element(By.CLASS_NAME, "pexOo")
            see_all_button.click()
        except NoSuchElementException:
            pass

        next_buttons = self.driver.find_elements(By.CLASS_NAME, "next")
        next_buttons[1].click()

    def get_all_restaurants(self):
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