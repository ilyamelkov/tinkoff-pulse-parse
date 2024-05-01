# **Tinkoff "Pulse" social network posts parsing**

## **Motivation**
- Social network for investors "Pulse" Tinkoff Investments is the largest social network for investors in Russia and the 6th in the world according to a [study by Trust Technologies (former PwC) in 2021](https://www.tinkoff.ru/about/news/09-12-2022-pulse-is-recognized-largest-social-network-for-investors-in-russia/)
- Data from "Pulse" can be used for sentiment analysis with regards to price fluctuations on a stock market
- As for now, "Pulse" social network doesn't have it's API which would allow people to extract data
- Existing solutions which I was able to find in the web did not satisfy my needs

## **Code logic explained**
- First, the code opens a page from web-archive. Finds a scroll length specifically for your screen which will trigger page refresh later on. 
- Then opens the corresponding forum page of a ticker of your choice and starts scrolling, using the parameter found in the previous step.
- Scrolls until the total page length will not exceed the desired page length provided by the user.
- Collects all the posts, dates and time data into a table.
- Saves resulting table in .csv format into a folder in your current working directory called parsed_data which will be created automatically.
- **NOTE:** If you already have a .csv file for your ticker, it will be automatically updated with new posts.

## **Functions description**
All functions are located in one python file called tinkoff_parse.py

- pulse_parse(caps_tick, stop_len):
  -  Main function, does everything what is described in above section about the logic of code. Existance of 'parsed_data' folder is also checked within this function
  - **Note:** caps_tick variable can be either a string or a list.

- get_param():
  - Finds the scrolling parameter. The page structure implies infinite scrolling and so page refresh is triggered at some point of scrolling. The whole code works on pixel scrolling, and so depending on the screen size, this parameter might vary.

- scroll_get_html(ticker, fin_p_len, scroll_up):
  - Opens the page with messages related to a ticker and scrolls down until desired page length is reached

- create_df(p_source):
  - Creates pandas dataframe from the page html with the following columns: posts, date, time 

- create_pulse_link(caps_tick):
  - Creates a link to Tinkoff social network from a ticker name

- format_date(df, col_name):
  - Formats the date in a dataframe to yyyy-mm-dd format.

- check_add_create_file(p_fname_fmt, df):
  - Checks whether the file with the ticker exists in parsed_data folder. Creates it, if a file doesn't exist or updates it if it exists.     
