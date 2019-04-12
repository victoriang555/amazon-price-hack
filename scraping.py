from selenium import webdriver
import os
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import pickle
import time
import numpy as np



# DEAD FUNCTION
def make_list_of_deals(num_of_items):
    deal_view_list = []
    for num in range(2, num_of_items + 1):
        deal_view = '100_dealView_{}'.format(num)
        deal_view_list.append(deal_view)
    return deal_view_list


# Click to the next products listings page
def click_to_next_page(driver, original_products_listing_page, deal_image_list, num_of_listing_pages):
    driver.get(original_products_listing_page)
    for listing_page in num_of_listing_pages:
        get_hrefs(deal_image_list)
        #pull_features_per_product_page(driver, list_of_pages[1:2])
        navigation_bar = driver.find_element_by_id('pagination-next-5257912710445445')
        next_button = navigation_bar.get_attribute('href')
        time.sleep(np.random.randint(10,15))
        next_button.click()
        time.sleep(np.random.randint(3,5))
    return

# Make a list of the urls for each of the products listed on the products listings page 
def get_hrefs(deal_image_list):
    list_of_pages = []
    for deal_image_item in deal_image_list:
        list_of_pages.append(deal_image_item.get_attribute('href'))
    return list_of_pages

# Obtain the list price from a product page 
def get_list_price(driver, locator, locator_backup):
    try:
        element_text = driver.find_element_by_id(locator).text
        element_data = float(element_text[1:])
    except:
        try:
            element_text = driver.find_element_by_id(locator_backup).text
            element_list = element_text.split('-')
            start_price_string = element_list[0].strip()
            end_price_string = element_list[1].strip()
            start_price_float = float(start_price_string[1:])
            end_price_float = float(end_price_string[1:])
            element_data = (end_price_float + start_price_float)/2
        except:
            element_text = driver.find_element_by_id(locator_backup).text
            element_data = float(element_text[1:])
    return element_data


# Obtain the sale price from a product page
def get_deal_price(driver, locator):
    try:
        element_text = driver.find_element_by_id(locator).text
        element_data = float(element_text[1:])
    except:
        element_data = None
    return element_data


# Obtain an element from a product page
def try_to_get_element_data(driver, locator, is_xpath=False, need_title=False, icon_id_prime=False):
    try:
        if is_xpath:
            element_data = driver.find_element_by_xpath(locator).text
        elif need_title:
            element_data = driver.find_element_by_id(locator).get_attribute('title')
        elif icon_id_prime:
            try:
                driver.find_element_by_id(locator)
                element_data = 'Prime'
            except:
                element_data = 'Not Prime'
        else:
            element_data = driver.find_element_by_id(locator).text
    except NoSuchElementException:
        element_data = None

    return element_data


# Get the asin, the unique Amazon product id 
# Since asin and list date same container, obtain both at once and then split them by line
def get_asin_and_list_date(driver) -> list:
    container_locator = '#detailBullets_feature_div ul'
    container = driver.find_elements_by_css_selector(container_locator)
    if len(container) > 0:
        try:
            needed_list_text = container[0].text
            asin_and_list_date = needed_list_text.splitlines()
        except:
            asin_and_list_date = None
    else:
        asin_and_list_date = None
    return asin_and_list_date


# Clean the asin text to just get the number 
def get_asin(driver):
    try:
        asin_and_list_date = get_asin_and_list_date(driver)
        asin_long = [i for i in asin_and_list_date if 'ASIN: ' in i]
        a = 'ASIN: '
        asin = asin_long[0][len(a):]
    except:
        asin = None
    return asin


# Clean the list date text to just get the date
def get_list_date(driver):
    try:
        asin_and_list_date = get_asin_and_list_date(driver)
        list_date_long = [i for i in asin_and_list_date if 'Date first available at Amazon.com: ' in i]
        a = 'Date first available at Amazon.com: '
        list_date = list_date_long[0][len(a):]
    except:
        list_date = None
    return list_date


# Clean the average customer review text to just get the number of stars as a float
def get_avg_cust_review(driver, locator):
    try:
        avg_cust_review_long = driver.find_element_by_id(locator).get_attribute('title')
        a = ' out of 5 stars'
        avg_cust_review = float(avg_cust_review_long[:-len(a)])
    except:
        avg_cust_review = None
    return avg_cust_review


# Clean the number of answered questions text to just get the number as an int
def get_num_answered_questions(driver, locator):
    try:
        num_answered_questions_string = driver.find_element_by_id(locator).text
        a = ' answered questions'
        num_answered_questions = int(num_answered_questions_string[:-len(a)])
    except:
        num_answered_questions = None
    return num_answered_questions


# Clean the seller rank text to just get the seller rank and category
'''The reason I didn't clean the category section of string is sometimes a page of product listings would include non-clothing/jewelry/shoes items. I thus needed to be able to identify and remove those when I cleaned my data later on. ''' 
def get_seller_rank(driver, locator, locator_backup):
    try:
        try:
            seller_rank_string = driver.find_element_by_id(locator).text.splitlines()
            beginning = 'Amazon Best Sellers Rank: #'
            seller_rank = seller_rank_string[0][len(beginning):]
        except:
            seller_rank_string = driver.find_element_by_id(locator_backup).text.splitlines()
            beginning = 'Amazon Best Sellers Rank: #'
            seller_rank = seller_rank_string[0][len(beginning):]
    except:
        seller_rank = None
    return seller_rank


# Cleaned the other sellers prices text to just get those list prices
def get_other_sellers_prices(driver, locator):
    try:
        other_sellers_string = driver.find_element_by_id(locator).text.splitlines()
        other_seller_prices_long = other_sellers_string[2::2]
        other_seller_prices_short = other_seller_prices_long[0::2]
        other_seller_prices = []
        for price in other_seller_prices_short:
            other_seller_prices.append(float(price[1:]))
    except:
        other_seller_prices = None
    return other_seller_prices


# Obtain product specifications bullets or identify whether a product specifications image was used instead
def get_product_specs(driver, locator, locator_backup):
    try:
        try:
            product_specs = driver.find_element_by_id(locator).text.splitlines()
        except:
            product_specs_listing = driver.find_element_by_id(locator_backup)
            product_specs = 'Product Specs Box Used'
    except:
        product_specs = None
    return product_specs


# Create a dataframe of all the product info
def pull_features_per_product_page(driver, list_of_pages):
    list_of_features = ['asin', 'item_description', 'num_cust_reviews', 'prime', 'list_price', 'deal_price',
                        'seller_rank', 'avg_cust_review', 'product_specs', 'bullets_in_description',
                        'num_answered_questions', 'expedited_shipping', 'lowest_other_used_price',
                        'other_sellers', 'amazon_choice', 'list date']
    all_features_values = []

    for page in list_of_pages:
        driver.get(page)
        try:
            try:
                asin = get_asin(driver)
                item_description = try_to_get_element_data(driver, 'productTitle')
                num_cust_reviews = try_to_get_element_data(driver, '//*[@id="reviewSummary"]/div[1]/a/div/div/div[2]/div/span',
                                                           is_xpath=True)
                prime = try_to_get_element_data(driver, 'priceBadging_feature_div', icon_id_prime=True)
                list_price = get_list_price(driver, 'priceblock_saleprice', 'priceblock_ourprice')
                deal_price = get_deal_price(driver, 'priceblock_dealprice')
                seller_rank = get_seller_rank(driver, 'dpx-amazon-sales-rank_feature_div', 'SalesRank')
                avg_cust_review = get_avg_cust_review(driver, 'acrPopover')
                product_specs = get_product_specs(driver, 'productDescription', 'dp-container')
                bullets_in_description = try_to_get_element_data(driver, 'feature-bullets')
                num_answered_questions = get_num_answered_questions(driver, 'askATFLink')
                expedited_shipping = try_to_get_element_data(driver, 'fast-track-message')
                lowest_other_used_price = try_to_get_element_data(driver, 'usedPrice')
                # Example of other_sellers: https://smile.amazon.com/Players-Handbook-Dungeons-Dragons-Wizards/dp/0786965606/ref=sr_1_6?s=books&ie=UTF8&qid=1524252967&sr=1-6&refinements=p_n_condition-type%3A1294425011
                other_sellers_prices= get_other_sellers_prices(driver, 'mbc')
                # example of amazon's choice : https://smile.amazon.com/Choice-Organic-Mental-Focus-Wellness/dp/B00E0C6DXM/ref=sr_1_16_a_it?ie=UTF8&qid=1524177671&sr=8-16&keywords=amazon%2Bchoice%2Bproducts&th=1
                amazon_choice = try_to_get_element_data(driver, 'acBadge_feature_div')
                list_date = get_list_date(driver)
                page_feature_values = [asin, item_description, num_cust_reviews, prime, list_price,
                                       deal_price, seller_rank, avg_cust_review, product_specs, bullets_in_description,
                                       num_answered_questions, expedited_shipping, lowest_other_used_price, other_sellers_prices,
                                       amazon_choice, list_date]
                all_features_values.append(page_feature_values)
                raw_df = pd.DataFrame(all_features_values, columns=list_of_features)
            except:
                item = driver.find_element_by_css_selector('.a-link-normal .a-text-normal')
                time.sleep(np.random.randint(5,10))
                item.click()
                asin = get_asin(driver)
                item_description = try_to_get_element_data(driver, 'productTitle')
                num_cust_reviews = try_to_get_element_data(driver, '//*[@id="reviewSummary"]/div[1]/a/div/div/div[2]/div/span',
                                                           is_xpath=True)
                prime = try_to_get_element_data(driver, 'priceBadging_feature_div', icon_id_prime=True)
                list_price = get_list_price(driver, 'priceblock_saleprice', 'priceblock_ourprice')
                deal_price = get_deal_price(driver, 'priceblock_dealprice')
                seller_rank = get_seller_rank(driver, 'dpx-amazon-sales-rank_feature_div', 'SalesRank')
                avg_cust_review = get_avg_cust_review(driver, 'acrPopover')
                product_specs = get_product_specs(driver, 'productDescription', 'dp-container')
                bullets_in_description = try_to_get_element_data(driver, 'feature-bullets')
                num_answered_questions = get_num_answered_questions(driver, 'askATFLink')
                expedited_shipping = try_to_get_element_data(driver, 'fast-track-message')
                lowest_other_used_price = try_to_get_element_data(driver, 'usedPrice')
                # Example of other_sellers: https://smile.amazon.com/Players-Handbook-Dungeons-Dragons-Wizards/dp/0786965606/ref=sr_1_6?s=books&ie=UTF8&qid=1524252967&sr=1-6&refinements=p_n_condition-type%3A1294425011
                other_sellers_prices= get_other_sellers_prices(driver, 'mbc')
                # example of amazon's choice : https://smile.amazon.com/Choice-Organic-Mental-Focus-Wellness/dp/B00E0C6DXM/ref=sr_1_16_a_it?ie=UTF8&qid=1524177671&sr=8-16&keywords=amazon%2Bchoice%2Bproducts&th=1
                amazon_choice = try_to_get_element_data(driver, 'acBadge_feature_div')
                list_date = get_list_date(driver)
                page_feature_values = [asin, item_description, num_cust_reviews, prime, list_price,
                                       deal_price, seller_rank, avg_cust_review, product_specs, bullets_in_description,
                                       num_answered_questions, expedited_shipping, lowest_other_used_price, other_sellers_prices,
                                       amazon_choice, list_date]
                all_features_values.append(page_feature_values)
                raw_df = pd.DataFrame(all_features_values, columns=list_of_features)
        except:
            raw_df = ''
            continue
    return raw_df


# In order to view the prime icon for a product, you need to login to your prime account 
# This will prompt the person running the script to login and send the credentials to Amazon
def enter_password(driver):
    driver.get('https://www.amazon.com/ap/signin?openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin%26_encoding%3DUTF8&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&&openid.pape.max_auth_age=0')
    email = input('Please enter your amazon email')
    email = email.strip()
    email_box = driver.find_element_by_id('ap_email')
    email_box.send_keys(email)
    continue_box = driver.find_element_by_id('continue')
    continue_box.click()
    password = input('Please enter your amazon password')
    password = password.strip()
    password_box = driver.find_element_by_id('ap_password')
    password_box.send_keys(password)
    signin_box = driver.find_element_by_id('signInSubmit')
    signin_box.click()


# My main function, which will kick off the whole script 
# Amazon would start suspending pages after scraping to products listings pages, so I scraped two at a time
def main():
    original_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_2?node=9538491011&nocache=1524333593751&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:2,sortOrder:BY_SCORE,dealsPerPage:32&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=AN5J01FTYBSBFDP82JSK&ie=UTF8'
    second_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_2?node=9538491011&nocache=1524333593751&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:2,sortOrder:BY_SCORE,dealsPerPage:32&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=AN5J01FTYBSBFDP82JSK&ie=UTF8'
    third_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_3?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:3,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=7RXS1XK2BPKZXJZ9GX41&ie=UTF8'
    fourth_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_5?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:5,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=3A8CZMB5K05YEGJS6F2F&ie=UTF8'
    fifth_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_6?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:6,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=3A8CZMB5K05YEGJS6F2F&ie=UTF8'
    sixth_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_7?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:7,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=3A8CZMB5K05YEGJS6F2F&ie=UTF8'
    seventh_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_8?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:8,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=3A8CZMB5K05YEGJS6F2F&ie=UTF8'
    eigth_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_9?node=9538491011&nocache=1524167558575&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:9,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=3A8CZMB5K05YEGJS6F2F&ie=UTF8'
    ninth_listing_page = 'https://smile.amazon.com/fashion-sales-and-deals/b/ref=gbps_ftr_m15_3ccc_page_10?node=9538491011&nocache=1524332320619&gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,page:10,sortOrder:BY_SCORE,dealsPerPage:48&pf_rd_p=dea43efa-ec24-4825-a635-85269d433ccc&pf_rd_s=merchandised-search-15&pf_rd_t=101&pf_rd_i=9538491011&pf_rd_m=ATVPDKIKX0DER&pf_rd_r=ME4CAD511E3872PQ3NWB&ie=UTF8'

    chromedriver = "/Applications/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    driver.set_window_size(1920, 1080)
    enter_password(driver)

    # driver.get(second_listing_page)
    # deal_image_list = driver.find_elements_by_id('dealImage')
    # list_of_pages = get_hrefs(deal_image_list)
    # # Slice the list_of_pages list to specify the number of pages you actually want to open and pull data for
    # final_df_pg2redo = pull_features_per_product_page(driver, list_of_pages[1:40])
    # final_df_pg2redo.to_json('data_pg2redo.json')
    # with open('final_df_pg2redo.pkl', 'wb') as picklefile:
    #     pickle.dump(final_df_pg2redo, picklefile)

    driver.get(original_listing_page)
    deal_image_list = driver.find_elements_by_id('dealImage')
    list_of_pages = get_hrefs(deal_image_list)
    # Slice the list_of_pages list to specify the number of pages you actually want to open and pull data for
    final_df_pg1redo = pull_features_per_product_page(driver, list_of_pages[1:40])
    final_df_pg1redo.to_json('data_pg1redo.json')
    with open('final_df_pg1redo.pkl', 'wb') as picklefile:
        pickle.dump(final_df_pg1redo, picklefile)


    # Only use driver.quit() when you're done with the last list of pages, otherwise you need to keep logging in

    driver.quit()


main()
