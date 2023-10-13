# import required packages
from selenium import webdriver
from bs4 import BeautifulSoup

urls = [
    'https://www.youtube.com/channel/UC0RhatS1pyxInC00YKjjBqQ'
]

driver = webdriver.Chrome()
for url in urls:
    driver.get(f'{url}/videos?view=0&sort=p&flow=grid')
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, 'lxml')
    channel_name_html = soup.find('yt-formatted-string', id='text', class_='style-scope ytd-channel-name')
    titles_html = soup.findAll('yt-formatted-string', id='video-title')
    views_html = soup.findAll('span', class_='inline-metadata-item style-scope ytd-video-meta-block')
    channel_name = channel_name_html.text.replace(" ","_")
    title, view, date = [], [], []
    
    for i in range(len(titles_html)):
        title.append(titles_html[i].text)
        view.append(views_html[i*2].text)
        date.append(views_html[i*2+1].text)

print(title)
print(view)
print(date)



