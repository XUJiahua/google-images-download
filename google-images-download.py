# In[ ]:
#  coding: utf-8

###### Searching and Downloading Google Images to the local disk ######

# Import Libraries
import sys  # Importing the System Library
version = (3, 0)
cur_version = sys.version_info
if cur_version >= version:  # If the Current Version of Python is 3.0 or above
    # urllib library for Extracting web pages
    import urllib.request
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError
    from urllib.parse import quote
else:  # If the Current Version of Python is 2.x
    # urllib library for Extracting web pages
    import urllib2
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import quote
import time  # Importing the time library to check the time of code execution
import os
import argparse
import ssl
import datetime
from bs4 import BeautifulSoup
import json
from selenium import webdriver

# ref: https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python
def scroll_down_to_bottom(driver):
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
#         print("scroll down event")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        
        # Click show more button if any
        show_more_btn = driver.find_element_by_css_selector('#smb')
        try:
#             print(show_more_btn.get_attribute("outerHTML"))
            show_more_btn.click()
        except:
            x = 0

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def download_page_internal(driver, url):
    driver.get(url)
    scroll_down_to_bottom(driver)
    elem = driver.find_element_by_xpath("//*")
    page = elem.get_attribute("outerHTML")
    return page

def get_image_urls_from_html(raw_html):
    soup = BeautifulSoup(raw_html, "lxml")
    divs = soup.find_all('div', class_='rg_meta notranslate')
    return [json.loads(div.text)['ou'] for div in divs]

def get_all_items_from_url(url):
    try:
        options = webdriver.ChromeOptions()
        # MacOS
        # options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        # Linux chrome binary
        options.binary_location = '/usr/bin/google-chrome-stable'
        # comment headless argument for debugging/ visualization
        options.add_argument('headless')
        options.add_argument('window-size=1200x600')

        # add proxy, restarting chrome needed if not work
        http_proxy="localhost:8123"
        options.add_argument('--proxy-server={0}'.format(http_proxy))

        driver = webdriver.Chrome(chrome_options=options)
    
        raw_html = download_page_internal(driver, url)
        return get_image_urls_from_html(raw_html)
    except:
        return []
    finally:
        # close chrome driver by calling quit()
        driver.quit()

# Taking command line arguments from users
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keywords', help='delimited list input', type=str, required=False)
parser.add_argument('-u', '--url', help='search with google image URL', type=str, required=False)
parser.add_argument('-l', '--limit', help='delimited list input', type=str, required=False)
parser.add_argument('-x', '--single_image', help='downloading a single image from URL', type=str, required=False)
parser.add_argument('-o', '--output_directory', help='download images in a specific directory', type=str, required=False)
parser.add_argument('-d', '--delay', help='delay in seconds to wait between downloading two images', type=str, required=False)
parser.add_argument('-c', '--color', help='filter on color', type=str, required=False,
                    choices=['red', 'orange', 'yellow', 'green', 'teal', 'blue', 'purple', 'pink', 'white', 'gray', 'black', 'brown'])
parser.add_argument('-r', '--usage_rights', help='usage rights', type=str, required=False,
                    choices=['labled-for-reuse-with-modifications','labled-for-reuse','labled-for-noncommercial-reuse-with-modification','labled-for-nocommercial-reuse'])
parser.add_argument('-s', '--size', help='image size', type=str, required=False,
                    choices=['large','medium','icon'])
parser.add_argument('-t', '--type', help='image type', type=str, required=False,
                    choices=['face','photo','clip-art','line-drawing','animated'])
parser.add_argument('-w', '--time', help='image age', type=str, required=False,
                    choices=['past-24-hours','past-7-days'])

args = parser.parse_args()

if args.keywords:
    search_keyword = [str(item) for item in args.keywords.split(',')]
# setting limit on number of images to be downloaded
if args.limit:
    limit = int(args.limit)
else:
    limit = 100

#if single_image or url argument not present then keywords is mandatory argument
if args.single_image is None and args.url is None and args.keywords is None:
            parser.error('Keywords is a required argument!')

if args.output_directory:
    main_directory = args.output_directory
else:
    main_directory = "downloads"

if args.delay:
    try:
        val = int(args.delay)
    except ValueError:
        parser.error('Delay parameter should be an integer!')

#Building URL parameters
def build_url_parameters():
    built_url = "&tbs="
    counter = 0
    params = {'color':[args.color,{'red':'ic:specific,isc:red', 'orange':'ic:specific,isc:orange', 'yellow':'ic:specific,isc:yellow', 'green':'ic:specific,isc:green', 'teal':'ic:specific,isc:teel', 'blue':'ic:specific,isc:blue', 'purple':'ic:specific,isc:purple', 'pink':'ic:specific,isc:pink', 'white':'ic:specific,isc:white', 'gray':'ic:specific,isc:gray', 'black':'ic:specific,isc:black', 'brown':'ic:specific,isc:brown'}],
              'usage_rights':[args.usage_rights,{'labled-for-reuse-with-modifications':'sur:fmc','labled-for-reuse':'sur:fc','labled-for-noncommercial-reuse-with-modification':'sur:fm','labled-for-nocommercial-reuse':'sur:f'}],
              'size':[args.size,{'large':'isz:l','medium':'isz:m','icon':'isz:i'}],
              'type':[args.type,{'face':'itp:face','photo':'itp:photo','clip-art':'itp:clip-art','line-drawing':'itp:lineart','animated':'itp:animated'}],
              'time':[args.time,{'past-24-hours':'qdr:d','past-7-days':'qdr:w'}]}
    for key, value in params.items():
        if value[0] is not None:
            ext_param = value[1][value[0]]
            #print(value[1][value[0]])
            # counter will tell if it is first param added or not
            if counter == 0:
                # add it to the built url
                built_url = built_url + ext_param
                counter += 1
            else:
                built_url = built_url + ',' + ext_param
                counter += 1
    return built_url

############## Main Program ############
t0 = time.time()  # start the timer
#Download Single Image using a URL arg
if args.single_image:
    url = args.single_image
    try:
        os.makedirs(main_directory)
    except OSError as e:
        if e.errno != 17:
            raise
            # time.sleep might help here
        pass
    req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    response = urlopen(req, None, 15)
    image_name = str(url[(url.rfind('/')) + 1:])
    if '?' in image_name:
        image_name = image_name[:image_name.find('?')]
    if ".jpg" in image_name or ".png" in image_name or ".jpeg" in image_name or ".svg" in image_name:
        output_file = open(main_directory + "/" + image_name, 'wb')
    else:
        output_file = open(main_directory + "/" + image_name + ".jpg", 'wb')
        output_file = open(main_directory + "/" + image_name + ".jpg", 'wb')
        image_name = image_name + ".jpg"

    data = response.read()
    output_file.write(data)
    response.close()

    print("completed ====> " + image_name)
# or download multiple images based on keywords
else:
    # Download Image Links
    errorCount = 0
    i = 0
    if args.url:
        search_keyword = [str(datetime.datetime.now()).split('.')[0]]
    #print(search_keyword)
    while i < len(search_keyword):
        items = []
        iteration = "\n" + "Item no.: " + str(i + 1) + " -->" + " Item name = " + str(search_keyword[i])
        print(iteration)
        print("Evaluating...")
        search_term = search_keyword[i]
        dir_name = search_term + ('-' + args.color if args.color else '')

        # make a search keyword  directory
        try:
            if not os.path.exists(main_directory):
                os.makedirs(main_directory)
                time.sleep(0.2)
                path = str(dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
            else:
                path = str(dir_name)
                sub_directory = os.path.join(main_directory, path)
                if not os.path.exists(sub_directory):
                    os.makedirs(sub_directory)
        except OSError as e:
            if e.errno != 17:
                raise
                # time.sleep might help here
            pass

        j = 0

        params = build_url_parameters()
        #color_param = ('&tbs=ic:specific,isc:' + args.color) if args.color else ''
        # check the args and choose the URL
        if args.url:
            url = args.url
        else:
            url = 'https://www.google.com/search?q=' + quote(search_term) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch' + params + '&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'
        items = items + (get_all_items_from_url(url))
        print("Total Image Links = " + str(len(items)))

        # This allows you to write all the links into a test file. This text file will be created in the same directory as your code. You can comment out the below 3 lines to stop writing the output to the text file.
        info = open('logs', 'a')  # Open the text file called database.txt
        info.write(str(i) + ': ' + str(search_keyword[i - 1]) + ": " + str(items))  # Write the title of the page
        info.close()  # Close the file

        t1 = time.time()  # stop the timer
        total_time = t1 - t0  # Calculating the total time required to crawl, find and download all the links of 60,000 images
        print("Total time taken: " + str(total_time) + " Seconds")
        print("Starting Download...")

        ## To save imges to the same directory
        # IN this saving process we are just skipping the URL if there is any error
        k = 0      
        if len(items) < limit:
            limit = len(items)
        while (k < limit):
            try:
                req = Request(items[k], headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
                response = urlopen(req, None, 15)
                image_name = str(items[k][(items[k].rfind('/')) + 1:])
                if '?' in image_name:
                    image_name = image_name[:image_name.find('?')]
                if ".jpg" in image_name or ".png" in image_name or ".jpeg" in image_name or ".svg" in image_name:
                    output_file = open(main_directory + "/" + dir_name + "/" + str(k + 1) + ". " + image_name, 'wb')
                else:
                    output_file = open(main_directory + "/" + dir_name + "/" + str(k + 1) + ". " + image_name + ".jpg", 'wb')
                    image_name = image_name + ".jpg"

                data = response.read()
                output_file.write(data)
                response.close()

                print("completed ====> " + str(k + 1) + ". " + image_name)

                k = k + 1

            except IOError:  # If there is any IOError
                errorCount += 1
                print("IOError on image " + str(k + 1))
                k = k + 1

            except HTTPError as e:  # If there is any HTTPError
                errorCount += 1
                print("HTTPError" + str(k))
                k = k + 1

            except URLError as e:
                errorCount += 1
                print("URLError " + str(k))
                k = k + 1

            except ssl.CertificateError as e:
                errorCount += 1
                print("CertificateError " + str(k))
                k = k + 1

            if args.delay:
                time.sleep(int(args.delay))

        i = i + 1

    print("\n")
    print("Everything downloaded!")
    print("Total Errors: " + str(errorCount) + "\n")

# ----End of the main program ----#
# In[ ]:

