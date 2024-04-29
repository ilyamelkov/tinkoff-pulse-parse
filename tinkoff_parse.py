# Load packages

## Data scrapping & manipulation
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from lxml import html

## Time manipulations
import time
from datetime import datetime
import datetime

## System
import os

## Data manipulations
import pandas as pd
import numpy as np
import re


def pulse_parse(caps_tick, stop_len: int):
    """
    Creates dataframe for ticker {caps_tick} with following columns: posts, date, time, ticker.
     * caps_tick variable can be either a list or a string.
        - ex: pulse_parse('VKCO', stop_len = 100000)
        - ex: pulse_parse(['VKCO', 'SBER', 'LKOH'], stop_len = 300000)
    * stop_len variable is the length of a page, after which the code will stop scrolling

    Created dataframe is saved into the current working directory in a folder called 'parsed_data' under ticker name in a .csv format
    If such file already exists, it will be updated with new posts/dates/time

    """
    # Get right param
    scrollup = get_param()
    ## Case of one ticker
    if isinstance(caps_tick, str) == True:
        caps_tick = caps_tick.upper()
        ## Scroll & save page source
        source = scroll_get_html(
            ticker=caps_tick, fin_p_len=stop_len, scroll_up=scrollup
        )
        df = create_df(source)
        df = format_date(df, "time")
        df["ticker"] = caps_tick
        ## Check if there is a folder in your current working directory named 'parsed_data'
        if not os.path.exists("parsed_data"):
            os.makedirs("parsed_data")

        else:
            pass

        check_add_create_file(
            p_fname_fmt=f"{os.getcwd()}//parsed_data//{caps_tick.lower()}.csv", df=df
        )

    ## Case of many tickers
    elif isinstance(caps_tick, list) == True:
        for t in caps_tick:
            t = t.upper()
            ### Scroll & save page source
            source = scroll_get_html(ticker=t, fin_p_len=stop_len, scroll_up=scrollup)
            df = create_df(source)
            df = format_date(df, "time")
            df["ticker"] = t
            ### Save resulting dataframe
            if not os.path.exists("parsed_data"):
                os.makedirs("parsed_data")

            else:
                pass

            check_add_create_file(
                p_fname_fmt=f"{os.getcwd()}//parsed_data//{t.lower()}.csv", df=df
            )
            


def get_param():
    """
    Takes web-archive page of a pulse social network.
    Returns right parameter (integer) for scrolling from the bottom of the page based on your screen size.
    Code is based on pixel scrolling, so parameters may vary from device to device.
    This parameter is needed in order to trigger page refresh on the bottom of the page to keep crolling downwards
    """
    try:
        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.set_page_load_timeout(60)
        # Open the  web-archive link
        driver.get(
            "https://web.archive.org/web/20230208212008/https://www.tinkoff.ru/invest/stocks/SBER/pulse/"
        )
        time.sleep(1)
        # Get page length
        page_length = driver.execute_script("return document.body.scrollHeight")
        # Scroll to the bottom of the page
        driver.execute_script(f"window.scrollTo(0, {page_length});")
        time.sleep(1)
        # Find the element ('Похожие акции')
        element = driver.find_element(
            By.XPATH, "//h2[@class = 'SecurityBlockHeader__title_KUEiP']"
        )
        time.sleep(1)
        # Scroll to the element
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        scrollheight = driver.execute_script(
            "return window.pageYOffset + window.innerHeight"
        )
        # print(f"All page length: {page_length}\nHeight of a scroll: {scrollheight}\nScroll from bottom is: {page_length-scrollheight}")
        # Get how much you should scroll from the bottom to trigger an infinite page refresh
        res = page_length - scrollheight
        driver.quit()
        return res

    except TimeoutException:
        pass


def scroll_get_html(ticker: str, fin_p_len: int, scroll_up: int):
    """
    Opens the page with messages related to a ticker and scrolls down untill page length is not equal or greater than fin_p_len.
    Returns html as a result.
    Variables:
        * ticker -  name of a ticker
        * fin_p_len - lenght of a page after which the code stops
        * scrollup - parameter of scroll up from the bottom

    """
    driver = webdriver.Chrome()
    # Generate link
    link = create_pulse_link(ticker)
    driver.get(link)
    driver.set_page_load_timeout(30)
    driver.maximize_window()

    i = 0

    page_length = driver.execute_script("return document.body.scrollHeight")
    print(
        ticker, page_length, np.round(page_length / fin_p_len * 100, 2), "%", end="\r"
    )

    while i == 0:
        try:
            driver.execute_script(f"window.scrollTo(0, {page_length - scroll_up});")
            time.sleep(1)
            new_page_length = driver.execute_script("return document.body.scrollHeight")

            if page_length == new_page_length:
                driver.execute_script(f"window.scrollTo(0, {page_length - scroll_up});")
            else:
                page_length = driver.execute_script("return document.body.scrollHeight")
                print(
                    ticker,
                    page_length,
                    np.round(page_length / fin_p_len * 100, 2),
                    "%",
                    end="\r",
                )

            if page_length > fin_p_len:
                i = 1

        except TimeoutException:
            pass

        except KeyboardInterrupt:
            print(
                "Code was stopped manually, collecting html... Do not restart kernel, proceed to creating dataframe"
            )
            driver.page_source
            break

    return driver.page_source


def create_df(p_source: str):
    """

    Creates a dataframe from the page source, finds all posts and dates/time

    """
    soup = bs(p_source, "html.parser")
    posts = soup.find_all(
        "div", {"pulse-posts-by-ticker__ffTK6Z pulse-posts-by-ticker__ifTK6Z"}
    )
    dates = soup.find_all("div", {"class": "pulse-posts-by-ticker__cSULlZ"})

    posts = [post.text for post in posts]
    date = [date.text for date in dates]

    new_df = pd.DataFrame()
    new_df["posts"] = posts
    new_df["time"] = date
    return new_df


def create_pulse_link(caps_tick: str):
    """
    Generates link to Pulse social network page based on a ticker.

    """
    link = f"https://www.tinkoff.ru/invest/stocks/{caps_tick}/pulse/"
    return link


def format_date(df, col_name: str):
    """
    Reformats dates in a dataframe with posts to yyyy-mm-dd format
    """
    months = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }

    # Create a list of dates
    ago = []
    t_y = []
    time_l = []
    # For each date in a list
    for date in df[col_name]:
        d = date.split(" ")
        if len(d) == 5:
            dd, mm, yyyy = d[0], months[d[1]], d[2]
            date_str = f"{yyyy}-{mm}-{dd}"
            time_l.append(d[4])
            date_object = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            ago.append(date_object)
        # Dates of format 'Сегодня в...' or 'Вчера в ...' (Today at .../Yesterday at ...)
        elif len(d) == 3:
            t_y.append(d)
            time_l.append(d[2])

    ty_dates = []
    for i in t_y:
        if i[0] == "Вчера":
            tdelta = datetime.timedelta(days=1)
            date = max(ago) + tdelta
            ty_dates.append(date)

        elif i[0] == "Сегодня":
            tdelta = datetime.timedelta(days=2)
            date = max(ago) + tdelta
            ty_dates.append(date)

    fin_dates = ty_dates + ago
    s_dates = sorted(fin_dates, reverse=True)

    new_df = df.copy()
    new_df["date"] = s_dates
    new_df = new_df.drop("time", axis="columns")
    new_df["time"] = time_l
    return new_df


def check_add_create_file(p_fname_fmt: str, df):
    """
    Checks whether a file for a ticker exists in a folder
        - If it doesn't exist, it saves a .csv file in 'parse_data' folder
        - If it does, old and new data will be merged & duplicates will be deleted, resulting in an updated dataset
    Returns a message with number of new entries or notifies user that the dataframe was created for the first time

    """
    # If a file with such name DOESN'T EXIST, create it
    if os.path.isfile(f"{p_fname_fmt}") == False:
        df.to_csv(f"{p_fname_fmt}", index=False)
        msg = f"{p_fname_fmt} was created!"
    # If a file with such name EXISTS
    else:
        ## Count number of entries in an old df
        nrows_old = pd.read_csv(f"{p_fname_fmt}").shape[0]
        ## Overwrite existing file (append new dataframe)
        df.to_csv(f"{p_fname_fmt}", mode="a", index=False, header=False)
        ## Read new file
        df_dub = pd.read_csv(f"{p_fname_fmt}")
        ## Drop dublicating rows
        df_dub.drop_duplicates(subset=None, inplace=True)
        ## Count number of new entries in a new df
        nrows_new = df_dub.shape[0]
        ## Count number of new entries
        dif = nrows_new - nrows_old
        ## Save final dataframe
        df_dub.to_csv(f"{p_fname_fmt}", index=False)
        msg = f"{dif} NEW POSTS were added to the {p_fname_fmt}"

    print(msg)
