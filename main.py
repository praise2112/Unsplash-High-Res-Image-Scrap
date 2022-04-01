from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
import time
import re
import os
import random
import string
from tqdm import tqdm
import concurrent.futures
import json
import argparse
from itertools import product
from functools import partial


def init_driver():
  options = webdriver.FirefoxOptions()
  options.add_argument("--headless")
  service = Service('./geckodriver')
  return webdriver.Firefox(options=options, service=service)


def get_img_links(high_res_div, use_tqdm=True):
  anchor_tags = high_res_div.find_elements(By.TAG_NAME, "a")
  img_link_pattern = re.compile('.+\/photos\/.+\/download')
  if use_tqdm:
    return [(anchor_tag.get_attribute('href'), get_rand_string()) for anchor_tag in tqdm(anchor_tags)
            if bool(img_link_pattern.match(anchor_tag.get_attribute('href')))]
  else:
    return [(anchor_tag.get_attribute('href'), get_rand_string()) for anchor_tag in anchor_tags
            if bool(img_link_pattern.match(anchor_tag.get_attribute('href')))]


def download_img(scrap_dir, link):
  urlretrieve(link[0], f"{os.path.join(os.path.realpath(scrap_dir), link[1])}.jpg")


def download_images(config, links):
  # utilize multiple threads for faster downlaods
  with concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers) as pool:
    return list(tqdm(pool.map(partial(download_img, config.scrap_dir), links, chunksize=40), total=len(links)))


def get_rand_string(length=15):
  return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def generator():
  while True:
    yield


def scroll_to_bottom(driver):
  for i in range(80, 101):
    for j in range(11):
      driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {(i-(j/10))/100});")


def scrap(config):
  os.makedirs(config.scrap_dir, exist_ok=True)
  driver = init_driver()
  driver.maximize_window()
  driver.get("https://unsplash.com/images/stock/high-resolution")
  time.sleep(3)
  # get div containing high res images
  high_res_div_xpath = "/html/body/div/div/div[6]/div/div"
  high_res_div = driver.find_element(By.XPATH, high_res_div_xpath)
  # footer display to none
  footer = driver.find_element(By.XPATH, "/html/body/div/div/div[9]/div")
  driver.execute_script("arguments[0].style.display = 'none'; return arguments[0];", footer)
  # loading required images
  print("Loading required Images")
  load_more_xpath = "/html/body/div/div/div[8]/div[1]/button"
  load_more_button = driver.find_element(By.XPATH, load_more_xpath)
  load_more_button.click()

  pbar = tqdm(generator())
  for _ in pbar:
    links = []
    try:
      links = get_img_links(high_res_div, use_tqdm=True)
    except Exception as e:
      pass
    if len(links) >= config.num:
      break
    pbar.set_description(f"Loaded Images: {len(links)}")
    for _ in tqdm(range(min(50, int(config.num*0.1)))):
      scroll_to_bottom(driver)
      time.sleep(0.5)

  print("Scrapping img links")
  links = get_img_links(high_res_div)
  print("No of images found: ", len(links))

  with open('data.json', 'w', encoding='utf-8') as f:
    json.dump({"links": links}, f)

  print("Downloading Images")
  download_images(config, links[:config.num-1])
  driver.quit()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--num', type=int, required=False,
                      help='Total number of images to scrap', default=5000)
  parser.add_argument('--scrap_dir', type=str, required=False,
                      help='Folder to store the scrapped file', default=os.path.join("D:\\", "unsplash"))
  parser.add_argument('--max_workers', type=int, required=False,
                      help='Max num of workers when downloading', default=10)
  args = parser.parse_args()
  scrap(args)
