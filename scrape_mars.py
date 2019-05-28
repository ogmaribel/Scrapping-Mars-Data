import pandas as pd

from bs4 import BeautifulSoup
import requests
import pymongo

from splinter import Browser
from splinter.exceptions import ElementDoesNotExist




def init_browser(): 
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    #Define and visit the url from the news section
    url_news = 'https://mars.nasa.gov/news/'
    browser.visit(url_news)

    # Create and parse the HTML Object for news
    html_news = browser.html
    soup = BeautifulSoup(html_news, 'html.parser')

    # Collect the latest News Title and Paragraph Text
    news_title = soup.find('div', class_='content_title').find('a').text
    news_paragraph = soup.find('div', class_='article_teaser_body').text

    #Define and visit the url from the featured images section
    image_url_featured = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url_featured)

    # Create and parse the HTML Object for the featured image
    html_featured = browser.html
    soup = BeautifulSoup(html_featured, 'html.parser')

    # Retrievethe current Featured Mars image url  
    images = soup.find('div', class_='carousel_items').find("article").get("style")
    featured_image_url =images.replace('background-image: url(','').replace(');', '').replace(');', '').replace("'","")
    featured_image_url = f"https://www.jpl.nasa.gov{featured_image_url}"

    # Weather url
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(weather_url)

    # Create and parse the HTML Object for the featured image
    html_weather = browser.html
    soup = BeautifulSoup(html_weather, 'html.parser')

    # Find all tweets
    latest_tweets = soup.find_all('div', class_='js-tweet-text-container')

    # Get only the first tweet regarding weather
    weather=""
    for tweet in latest_tweets: 
        weather_tweet = tweet.find('p').text
        if 'Sol' and "high" and "low" and 'pressure' in weather_tweet:
            weather =weather+ weather_tweet
            break

    weather=weather.replace('\nwinds', ' winds')
    weather=weather.replace('\npressure', ' pressure')
    weather=weather.replace('.twitter.com/7XARGO6DS6', '')

    #Facts
    facts_url = 'http://space-facts.com/mars/'
    # Read with pandas
    facts = pd.read_html(facts_url)
    #Extract first element of the list to gather the dataframe
    facts_df = facts[0]
    facts_df = facts_df.rename(columns={0:"Description", 1:"Value"})
    facts_df.set_index("Description", inplace=True)
    facts_df_html=facts_df.to_html()

    # url for hemispheres 
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)

    # Create and parse the HTML Object 
    html_hemispheres = browser.html
    soup = BeautifulSoup(html_hemispheres, 'html.parser')

    # Call all the div containing the image and the description
    items = soup.find_all('div', class_='item')
    hemisphere_image_urls=[]

    for i in items: 
        hemisphere_title = i.find('h3').text
        
        # Store link that leads to full image website
        hemisphere_image = i.find('a', class_='itemLink product-item')['href']
        
        # Call the page were the jpg image is stored
        browser.visit('https://astrogeology.usgs.gov' + hemisphere_image)  
        big_img_html = browser.html
        soup = BeautifulSoup( big_img_html, 'html.parser')
        
        # Get the image
        jpg_image = 'https://astrogeology.usgs.gov' + soup.find('img', class_='wide-image').get('src')
        
        # Append the retreived information into a list of dictionaries 
        hemisphere_image_urls.append({"title" : hemisphere_title, "image" : jpg_image})
    

    # Store data in a dictionary
    storage = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image_url,
        "weather_data": weather,
        "mars_facts": facts_df_html,
        "hemispheres": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return storage
