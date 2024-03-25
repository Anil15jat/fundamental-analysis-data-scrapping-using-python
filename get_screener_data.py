from playwright.sync_api import sync_playwright
import pdb
import re
import argparse
import json
import yaml

global loginBypass
loginBypass = True

def get_screener_data():
    parser = argparse.ArgumentParser(description='Scrap fundamental data from screener.in')
    parser.add_argument('-cl', '--company_list', type=str, default="reliance,havells,TATACONSUM", help='Specify the list of companies for which data needs to be retrieved. i.e. - -cl "reliance,havells"')
    parser.add_argument('-u', '--user_name', type=str, default="", help='Specify username for login.')
    parser.add_argument('-p', '--password', type=str, default="", help='Specify password for login.')
    parser.add_argument('-url', '--url', type=str, default="https://www.screener.in/home/", help='Specify login page URL for screener.in.')
    parser.add_argument('-fd', '--file_directory', type=str, default="/tmp", help='Specify the path to save data in file.yaml format.')
    args = parser.parse_args()


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        global loginBypass
        if len(args.user_name) and len(args.password):
            print("Login into screener account")
            login_to_website(page, args.url, args.user_name, args.password)
            loginBypass = False
        # in case the company list is not parsed in expected format, fix few of the scenarios before consuming the argument values
        if " " in args.company_list:
            company_list_string = args.company_list.strip().replace(" ",",")
        else:
            company_list_string = args.company_list
        company_list = company_list_string.lstrip('[').rstrip(']').split(',')
        for company_name in company_list:
            if not len(company_name):
                continue
            company_data_dict = {}
            print(f"Navigating to company {company_name} page")
            go_to_company_url_screen(page,company_name)
            # import pdb; pdb.set_trace()
            company_data_dict["company_name"] = get_company_name(page)
            company_data_dict["about_company"] = get_about_company(page)
            company_data_dict["ratio"] = get_company_ratios(page)
            company_data_dict["peer_comparison"] = get_peer_comparison(page)
            company_data_dict["quarterly_result"] = get_quarterly_results(page)
            company_data_dict["profit_and_loss"] = get_profit_and_loss(page)
            company_data_dict["balance_sheet"] = get_balance_sheet(page)
            company_data_dict["cash_flow"] = get_cash_flows(page)
            company_data_dict["ratios"] = get_ratios(page)
            company_data_dict["quarterly_shareholding_patterns"] = get_shareholding_patterns(page,pattern_type="quarterly-shp")
            company_data_dict["profilt_loss_ranges_table_content"] = get_profilt_loss_ranges_table_content(page)
            # import pdb; pdb.set_trace()
            # yearly_shareholding_patterns_dict = get_shareholding_patterns(page,pattern_type="yearly-shp")
            print("######################")
            print(f"company_name : {company_name}")
            print(f"company_data_dict : {company_data_dict}")
            file_name = f'{args.file_directory.rstrip("/")}/{company_name.upper()}.txt'
            file_name_yaml = f'{args.file_directory.rstrip("/")}/{company_name.upper()}.yaml'
            with open(file_name, "w") as json_file:
                json_file.write(json.dumps(company_data_dict))
            with open(file_name_yaml, "w") as json_file_yaml:
                yaml.dump(
                    company_data_dict,
                    json_file_yaml,
                    default_flow_style=False,
                    sort_keys=True,
                )
                json_file_yaml.flush()
            # import pdb; pdb.set_trace()
        browser.close()

def login_to_website(page, url, username, password):
    page.goto(url)
    page.locator('//*//a[contains(@class,"button")][contains(@class,"account")][contains(@href,"login")]').click()
    page.fill('//*//input[contains(@name,"username")]',username)
    page.fill('//*//input[contains(@name,"password")]',password)
    page.locator('//*//button[contains(@type,"submit")]').click()

def go_to_company_url_screen(page, company_name):
    try:
        company_page_url = 'https://screener.in/company/company_name_string/consolidated'.replace("company_name_string",company_name.upper())
        print(f"Company url : {company_page_url}")
        page.goto(company_page_url)
    except Exception as err:
        print(f"Exception seen while navigating to company url {company_page_url}; Assertion : {err}")

def get_company_name(page):
    company_name = None
    try:
        company_name_xpath = '//*//h1[contains(@class,"show-from-tablet-landscape")]'
        company_name = page.locator(company_name_xpath).inner_text()
    except Exception as err:
        print(f"Exception seen while fetching company name; Assertion : {err}")
    return company_name

def get_company_ratios(page):
    ratio_dictionary = {}
    try:
        company_ratio_entry_xpath = '//*//div[contains(@class,"company-ratio")]//ul[contains(@id,"top-ratios")]/li//span[contains(@class,"name")]'
        ratio_name_xpath = company_ratio_entry_xpath + '[normalize-space(text())="ratio_name_string"]'
        ratio_number_xpath = ratio_name_xpath + '/..//span//span[contains(@class,"number")]'
        ratio_list = page.query_selector_all(company_ratio_entry_xpath)
        for ratio_element in ratio_list:
            ratio_name = ratio_element.inner_text()
            ratio_name_list = ratio_dictionary.setdefault(ratio_name,[])
            ratio_number_list = page.query_selector_all(ratio_number_xpath.replace("ratio_name_string",ratio_name))
            for ratio_number_element in ratio_number_list:
                ratio_name_list.append(ratio_number_element.inner_text())
            #ratio_dictionary[ratio_name] = ratio_number
    except Exception as err:
        print(f"Exception seen while fetching company ratios; Assertion : {err}")
    return ratio_dictionary

def get_about_company(page):
    company_about_content = None
    if loginBypass:
        print("Script is running without user account login. Skipping about company content scrapping.")
    else:
        try:
            company_about_read_more_xpath = '//*//button[contains(normalize-space(text()),"Read More")]'
            page.locator(company_about_read_more_xpath).click()
            company_about_content_xpath = '//*//div[contains(@class,"modal-content")]'
            company_about_content = page.locator(company_about_content_xpath).inner_text()
            close_company_about_xpath = '//*//div[contains(@class,"modal-header")]//button'
            page.locator(close_company_about_xpath).click()
        except Exception as err:
            print(f"Exception seen while fetching about company; Assertion : {err}")
    return company_about_content

def get_table_content(page,id):
    result_dict = {}
    try:
        table_xpath = '//*//section[contains(@id,"id_string")]'.replace("id_string",id)
        header_xpath = table_xpath + '//*//table//thead//tr'
        data_xpath = table_xpath + '//*//table[contains(@class,"data-table")]/tbody/tr'
        result_dict["header"] = get_all_elements_text(page,header_xpath)[0].split("\t")
        result_data_list = result_dict.setdefault("data",[])
        row_element_list = page.query_selector_all(data_xpath)
        for row in row_element_list:
            result_data_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching table content for table-id {id}; Assertion : {err}")
    return result_dict

def get_profilt_loss_ranges_table_content(page):
    result_dict = {}
    try:
        table_xpath = '//*//section[contains(@id,"profit-loss")]//div//table[contains(@class,"ranges-table")]'
        header_xpath = table_xpath + '//tbody//tr//th'
        custom_header_xpath = table_xpath + '//tbody//tr//th[contains(text(),"header_name_string")]'
        custom_data_xpath = custom_header_xpath + '/../..//tr'
        header_name_list = get_all_elements_text(page,header_xpath)
        for header_name in header_name_list:
            range_table_list = result_dict.setdefault(header_name,[])
            custom_data_xpath = custom_data_xpath.replace("header_name_string",header_name)
            row_element_list = page.query_selector_all(custom_data_xpath)
            for row in row_element_list:
                if header_name not in row.inner_text().split("\t"):
                    range_table_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching profile loss ranges table content; Assertion : {err}")
    return result_dict

def get_peer_comparison(page):
    peer_comparison_dict = {}
    try:
        peers_table_xpath = '//*//section[contains(@id,"peers")]'
        sector_xpath = peers_table_xpath + '//div//p'
        sector_details = page.locator(sector_xpath).inner_text()
        sector_pattern = re.compile(r'^\S+:+\s+(?P<sector_name>\S+)\s+\S+:+\s+(?P<industry_name>\S+)')
        pattern_match = sector_pattern.match(sector_details)
        if pattern_match:
            group = pattern_match.groupdict()
            peer_comparison_dict["sector"] = group["sector_name"]
            peer_comparison_dict["industry"] = group["industry_name"]
        peer_table_data_xpath = peers_table_xpath + '//*//table[contains(@class,"data-table")]/tbody/tr'
        peer_comparison_data_list = peer_comparison_dict.setdefault("data",[])
        row_element_list = page.query_selector_all(peer_table_data_xpath)
        for row in row_element_list:
            if "S.No." in row.inner_text().split("\t"):
                peer_comparison_dict["header"] = row.inner_text().split("\t")
            else:
                peer_comparison_data_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching peer comparison data; Assertion : {err}")
    return peer_comparison_dict

def get_all_elements_text(driver, elem_xpath, timeout=30000):
    text_list = []
    try:
        driver.wait_for_selector(elem_xpath, timeout=timeout)
        element_list = driver.query_selector_all(elem_xpath)
        for element in element_list:
            text_list.append(element.inner_text())
    except Exception as e:
        print(f"Failed to get element text - {e}")
    return text_list

def get_quarterly_results(page):
    quarterly_result_dict = {}
    try:
        quarterly_result_table_xpath = '//*//section[contains(@id,"quarters")]'
        quarterly_result_header_xpath = quarterly_result_table_xpath + '//*//table//thead//tr'
        quarterly_result_data_xpath = quarterly_result_table_xpath + '//*//table[contains(@class,"data-table")]/tbody/tr'
        quarterly_result_dict["header"] = get_all_elements_text(page,quarterly_result_header_xpath)[0].split("\t")
        quarterly_result_data_list = quarterly_result_dict.setdefault("data",[])
        row_element_list = page.query_selector_all(quarterly_result_data_xpath)
        for row in row_element_list:
            if "Raw PDF" not in row.inner_text().split("\t"):
                quarterly_result_data_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching quarterly result data; Assertion : {err}")
    return quarterly_result_dict

def get_profit_and_loss(page):
    profit_and_loss_dict = {}
    try:
        profit_and_loss_table_xpath = '//*//section[contains(@id,"profit-loss")]'
        profit_and_loss_header_xpath = profit_and_loss_table_xpath + '//*//table//thead//tr'
        profit_and_loss_data_xpath = profit_and_loss_table_xpath + '//*//table[contains(@class,"data-table")]/tbody/tr'
        profit_and_loss_dict["header"] = get_all_elements_text(page,profit_and_loss_header_xpath)[0].split("\t")
        profit_and_loss_data_list = profit_and_loss_dict.setdefault("data",[])
        row_element_list = page.query_selector_all(profit_and_loss_data_xpath)
        for row in row_element_list:
            if "Raw PDF" not in row.inner_text().split("\t"):
                profit_and_loss_data_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching profit and loss data; Assertion : {err}")
    return profit_and_loss_dict

def get_balance_sheet(page):
    return get_table_content(page,"balance-sheet")

def get_cash_flows(page):
    return get_table_content(page,"cash-flow")

def get_ratios(page):
    return get_table_content(page,"ratios")

def get_shareholding_patterns(page,pattern_type="quarterly-shp"):
    result_dict = {}
    try:
        table_xpath = '//*//section[contains(@id,"shareholding")]//div[contains(@id,"pattern_type")]'.replace("pattern_type",pattern_type)
        header_xpath = table_xpath + '//*//table//thead//tr'
        data_xpath = table_xpath + '//*//table[contains(@class,"data-table")]/tbody/tr'
        result_dict["header"] = get_all_elements_text(page,header_xpath)[0].split("\t")
        result_data_list = result_dict.setdefault("data",[])
        row_element_list = page.query_selector_all(data_xpath)
        for row in row_element_list:
            result_data_list.append(row.inner_text().split("\t"))
    except Exception as err:
        print(f"Exception seen while fetching shareholding pattern data; Assertion : {err}")
    return result_dict

# def get_concall_content(page):
#     concall_xpath = '//*//div[contains(@class,"concalls")]'
#     concall_read_more_xpath = concall_xpath + '//*//button[contains(@class,"show-more-button")]'
#     page.locator(concall_read_more_xpath).click()
#     concall_list_links_xpath = concall_xpath + '//*//ul[contains(@class,"list-links")]/li'
#     notes_xpath = 
#     pass


if __name__ == "__main__":
    get_screener_data()

