from bs4 import BeautifulSoup
import requests

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')
    
def get_manga_info(url):
    soup = get_soup(url)
    info = soup.select('div a[href*="/title/"]')
    image = soup.select_one('div img')
    return [info[0].text, image['src'], info[3].text]