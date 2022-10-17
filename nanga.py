import requests
import os
from bs4 import BeautifulSoup 
from  selenium import webdriver
import pandas as pd
from googletrans import Translator

def get_driver():
    print("initializing driver ...")
    chrome_options = webdriver.ChromeOptions()
    current_directory = os.getcwd()
    driver_path = os.path.join(current_directory, "chromedriver.exe")
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options, executable_path=driver_path)
    print("finish initializing driver !!!")
    return driver

def get_str_to_number(inp_str):
    num = ""
    for c in inp_str:
        if c.isdigit():
            num = num + c
    return num

def get_title(soup):
    title = soup.find_all("h3",{"class":"font-heading heading-case text-headings break-anywhere text-h4 leading-none mb-2"})[1].text
    translator = Translator()
    title = translator.translate(title, dest = "en").text
    return title

def get_options(soup):
    size_tag = "-mb-3"
    color_tag = "-mb-1"
    div = soup.find_all("div",{"data-name":"options"})
    color = div[0].find_all("div", {"class":"-mb-1"})
    size = div[0].find_all("div", {"class":"-mb-3"})
    if(len(color) != 0):
        color_options = ""
        input_tag = color[0].find_all("input")
        for color in input_tag:
            color_options = color_options + color["value"] +"\n"
        color_options = color_options[:-1]
        translator = Translator()
        color_options = translator.translate(color_options, dest = "zh-tw").text
    else:
        color_options = ""

    if(len(size) != 0):
        size_options = ""
        input_tag = size[0].find_all("input")
        for size in input_tag:
            size_options = size_options + size["value"]+ "\n"
        size_options = size_options[:-1]  
        translator = Translator()
        size_options = translator.translate(size_options, dest = "en").text  
    else:
        size_options = ""
    return [color_options, size_options]

def get_price(soup):
    price = soup.find_all("span",{"class":"money text-h4 font-heading heading-case leading-none"})[1].text
    price = get_str_to_number(price)
    return price

def get_intro(soup):
    intro = ""
    div = soup.find_all("div",{"class":"animate-details-content"})[2]
    p = div.find_all("p")
    for p in p:
        strong = p.find_all("strong")
        span = p.find_all("span")
        if len(strong) != 0:
            intro = intro + strong[0].text + "\n"
        if len(span) != 0:
            intro = intro + span[0].text + "\n"
    translator = Translator()
    intro = translator.translate(intro, dest = "zh-tw").text
    return intro

def get_spec(soup):
    div = soup.find_all("div",{"data-name":"size-chart"})[0]
    p = div.find_all("p")
    if(len(p) > 1):
        p = p[1:]

    strong = p[0].find_all("strong")
    strong_items = []
    for i in strong:
        s = str(i).replace("<strong>","").replace("</strong>","")
        if s != "〈アイテム詳細〉":
            strong_items.append(s)

    span = p[0].find_all("span")
    span_items = []
    for i in span:
        s = str(i).replace("<span>","").replace("</span>","")
        span_items.append(s)

    spec_table = ""
    for idx, i in enumerate(strong_items):
        spec_table = spec_table + i + " : " + span_items[idx] + "\n"

    translator = Translator()
    spec_table = translator.translate(spec_table, dest = "zh-tw").text
    return spec_table

def get_spec_2(soup):
    div = soup.find_all("div",{"data-name":"size-chart"})
    li = div[0].find_all("li")
    spec_table = ""
    replace_words = [
        "<strong>",
        "</strong>",
        "<li>",
        "</li>",
        "\n",
        "<span>",
        "</span>",
        '<span color="#000000">',
        "<b>",
        "</b>",
        ]
    for i in li :
        item = str(i)
        for word in replace_words:
            if word in item:
                item = item.replace(word,"")
        item = item.replace("<br/>"," : ")
        spec_table = spec_table + item + "\n"
    translator = Translator()
    spec_table = translator.translate(spec_table, dest = "zh-tw").text
    return spec_table


def get_meta_data(driver, url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    try:
        title = get_title(soup)
    except:
        print("get title failed")
        title = "not found"
    try:
        options = get_options(soup)
    except:
        print("get options failed")
        options = ["",""]
    color_options = options[0]
    size_options = options[1]

    try:
        price = get_price(soup)
    except:
        print("get price failed ")
        price = "not found"
    
    try:
        intro = get_intro(soup)
    except:
        print("get intro failed")
        intor = ""
    # get image
    try:
        get_image(title,soup)
    except:
        print("get image failed")
        pass
    
    # get spec table
    try:
        spec_table = get_spec(soup)
    except:
        try:
            spec_table = get_spec_2(soup)
        except:
            spec_table = ""
    return [title, url, color_options, size_options, intro, spec_table, price] 

def get_image(folder_name, soup):
    current_directory = os.getcwd()
    new_directory = os.path.join(current_directory, "image")
    new_directory = os.path.join(new_directory, folder_name)
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    img_url_list = []
    div = soup.find_all("div",{"class":"w-full bg-page lg:pt-5"})
    img = div[0].find_all("img")
    for i in img:
        img_url_list.append("https:"+i["src"])
    for idx, url in enumerate (img_url_list):
        img_data = requests.get(url).content
        file_name = new_directory+"/"+str(idx)+".jpg"
        with open(file_name, 'wb') as handler:
            handler.write(img_data)
    return

def get_url_list(filename):
    f = open(filename, "r")
    url_list = f. readlines()
    f.close()
    for idx, i in enumerate(url_list):
        url_list[idx] = i.replace("\n","")
    return url_list

