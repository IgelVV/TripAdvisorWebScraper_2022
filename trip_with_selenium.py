import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
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

    categories = {
        'hotels': None,
        'restaurants': None
    }

    def __init__(self, driver, url):
        self.driver = driver
        self.url = url

    def parse(self):
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
        print(self.categories)

    def get_all_hotels(self):
        self.driver.get(self.url)
        hotels_button = self.driver.find_element(By.CLASS_NAME, "XUWut Ra _S z _Z w o v _Y Wh k _T wSSLS")

    def get_all_restaurants(self):
        ...


def main():
    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={useragent}')
    driver = webdriver.Chrome(executable_path=r'chromedriver', options=options)

    try:
        parser = TripAdvisorParser(driver, URL)
        parser.get_links_to_site_categories()
        # driver.maximize_window()
    except Exception as e:
        print(e)
    finally:
        driver.close()
        driver.quit()


if __name__ == '__main__':
    main()