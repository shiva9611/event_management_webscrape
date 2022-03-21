import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
from datetime import datetime
import logging as lg


ref_url = 'https://www.eventbrite.com/d/india--bangalore/free--health--events--this-month/?page=1'

header1 = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

proxy = {'http://':'194.233.69.90:443' , 'https://':'194.233.69.90:443'}

##This is used to store the all the links that is for different regions and event categories
base_url_loc_cat = []

    

def category_links():
    """
    This method is created for creating the list of urls with categories as shared in the ref_url
    :return:[url1,url2,..]
    """
    for i in ['bangalore','mumbai','chennai']:
        for j in ['business--classes','food-and-drink--events','health--events','music--events','auto-boat-and-air--events','charity-and-causes--events','community--events','family-and-education--events','fashion--events','film-and-media--events','hobbies--events','home-and-lifestyle--events','arts--events','government--events','spirituality--events','school-activities--events','science-and-tech--events','holiday--events','sports-and-fitness--events','travel-and-outdoor--events','other--events']:
                base_url_loc_cat.append((f'https://www.eventbrite.com/d/india--{i}/free--{j}--this-month/?page=1',i,j))



def no_pages(url, proxy=proxy, header1=header1):
    """

    :param url: This send the main page url which is stored in the base_url_loc_cat
    :param proxy:
    :param header1:
    :return: int(page) this will give us the total number of pages .
    """

    page = 0
    try:
        ever1 = req.get(url, proxies=proxy, headers=header1)
        soup = bs(ever1.content, 'lxml')
        page = soup.find_all('li', class_='eds-pagination__navigation-minimal eds-l-mar-hor-3')[0].text[-1]

    except:
        page = 0
    finally:
        return int(page)
    


def response_url(url, proxy=proxy, header1=header1):
    """
    This function is built send the response with resource from that url if status is 200 then only it wil
    send the response otherwise it will retry
    :param url: url
    :param proxy:
    :param header1:
    :return: the response
    """
    ever1 = req.get(url, headers=header1, proxies=proxy)
    if ever1.status_code == 200:
        return ever1
    else:
        response_url(url, proxy, header1)


##To get the unique urls in current page
def unique(url):
    """
    This is method is used for to get the unique events details only in that page
    :param url:
    :return: list of url
    """
    s=set()
    for i in url:
        s.add(i.a['href'])
    return list(s)

#If we need to traverse on the all the pages in the we need to parameterize all the


def get_urls(url,header1=header1, proxy=proxy):
    """
    This method is for getting the event urls inside the main page
    :param url: url ( base url)
    :param header1:
    :param proxy:
    :return: list of event urls
    """
    event_urls = []
    baseurl = url
    page = int(no_pages(baseurl,proxy,header1)) + 1
    if page == 1:
        pass
    else:
        for i in range(1, page):
            url1=baseurl[:-1] + str(i)
            ever1 = req.get(url1, headers=header1, proxies=proxy)
            if ever1.status_code == 200:
                soup = bs(ever1.content, 'lxml')
                individual_event_link = soup.find_all("div", class_="eds-event-card-content__primary-content")
                event_urls = event_urls + unique(individual_event_link)
            else:
                exit()
    return event_urls


def urls_cat_loc(base_url_loc_cat):
    """
    This is the main method where we
    :param base_url_loc_cat:
    :return:
    """
    d = {}
    total_data = []
    for i in range(len(base_url_loc_cat)):
        url = base_url_loc_cat[i][0]
        urls = get_urls(url)
        if len(urls) == 0:
            pass
        else:
                for j in urls:
                    d = scrape(j)
                    #d['location']=base_url_loc_cat[i][1]
                    d['category'] = base_url_loc_cat[i][2]
                    total_data.append(d)
    return total_data


def scrape(page_url,resp_url=response_url,proxy=proxy, header1=header1):
    html_page=resp_url(page_url,proxy=proxy,header1=header1)
    soup = bs(html_page.content, 'lxml')
    try:
        title = soup.find('h1', class_="listing-hero-title").text
    except:
        title = "Not Available"
    try:
        organizer = soup.find('a', class_="js-d-scroll-to listing-organizer-name text-default").text.strip('\n\t').strip('by')
    except:
        organizer = 'Not Available'
    try:
        description = soup.find('div',
                            class_="structured-content-rich-text structured-content__module l-align-left l-mar-vert-6 l-sm-mar-vert-4 text-body-medium").text.strip(
        '\n\t')
    except:
        description = "Not Available"
    try:
        time = soup.find('div', class_='event-details__data')
        time1, time2 = time.find_all('meta')[0]['content'], time.find_all('meta')[1]['content']
    except:
        time1,time2 = ('Not Available','Not Availbale')
    try:
        tags = soup.find('div', class_='g-cell g-cell-10-12 g-cell-md-12-12')
        tags_list = [t.span.text for t in
                 tags.find_all('a', class_='js-d-track-link listing-tag badge badge--tag l-mar-top-2')]
    except:
        tags_list = 'Not Available'
    try:
        loc = soup.find('ul', class_='grouped-ico').find('a',
                                                     class_='btn btn--target is-collapsed js-drive-directions-link btn--invert')[
        'href']

        long, latit = loc.split('&daddr=')[1].split('&driving')[0].split(',')
    except:
        long, latit = ('NA','NA')
    try:
        event_details = soup.find('div',
                              class_='listing-map-card-body g-cell g-cell-1-1 g-cell-lg-8-12 g-cell--no-gutters l-pad-top-6 l-pad-bot-4')
        venue = event_details.h2.text.strip('\n\t').split('\n\t')[-1].strip('\t') + event_details.p.text.strip('\n\t')
    except:
        venue='Not Available'
    try:
        price = soup.find('div', class_="js-display-price").text.strip('\n\t')
    except:
        price='Not Available'
    try:
        hero_image = (soup.find('div',
                            class_='listing-hero listing-hero--ratio-one-two listing-hero--bkg clrfix fx--delay-6 fx--fade-in')).picture[
        'content']
    except:
        hero_image = 'Not Available'
    try:
        content_images = '|'.join([i['src'] for i in (soup.find_all('img', class_="structured-content__image g-img"))])
    except:
        content_images = 'Not Available'

    try:
        video_assets = '|'.join(
            [i['src'] for i in (soup.find_all('iframe', class_="structured-content-video__iframe"))])
    except:
        video_assets = 'Not Available'
    return {
        'url': page_url,
        'title':title,
        'description': description,
        'creator': organizer,
        'location_address': venue,
        'location_lat_lng': latit + '|' + long,
        'start_time':time1,
        'end_time': time2,
        'tags': tags_list,
        'hero_img': hero_image,
        'content_image': content_images,
        'video_assets': video_assets
    }


##function needs to be applied on the location_adress
def link_extractor(text):
    urls = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', text)
    if len(urls) > 0:
        if len(urls[0]) > 11:
            return urls[0]
        else:
            return "Not Available"
    else:
        return 'Not Available'

def data_cleaning(df):
    d = {'business--classes': 'Business Classes', 'food-and-drink--events': 'Food and Drink',
         'health--events': 'Helath', 'music--events': 'Music', 'auto-boat-and-air--events': 'Auto Boat and Air',
         'charity-and-causes--events': 'Charity and Causes', 'community--events': 'Community',
         'family-and-education--events': 'Family and Education', 'fashion--events': 'Fashion',
         'film-and-media--events': 'Film and Media', 'hobbies--events': 'Hobbies',
         'home-and-lifestyle--events': 'Home and Lifestyle', 'arts--events': 'Arts', 'government--events': 'Government',
         'spirituality--events': 'Spirituality', 'school-activities--events': 'School Activities',
         'science-and-tech--events': 'Science and Tech', 'holiday--events': 'Holiday',
         'sports-and-fitness--events': 'Sports ans Fitness', 'travel-and-outdoor--events': 'Travel and Outdoor',
         'other--events': 'Other'}
    df['category'] = df['category'].replace(d)
    df['location_online'] = df['location_address'].apply(link_extractor)
    df.drop_duplicates(['title', 'location_address', 'category'], inplace=True)

    return df

category_links()


data = urls_cat_loc(base_url_loc_cat)
df = pd.DataFrame(data=data, columns=list(data[0].keys()))
final_data = data_cleaning(df)

final_data.to_csv(f'india_region{datetime.now().strftime("%d-%m-%Y-%H-%M")}.csv')
