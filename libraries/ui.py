import os
import pandas as pd

from RPA.Browser.Selenium import Selenium
from selectorlib import Extractor

from libraries import common as com
from libraries.pdf import PDFParser
from envs import OUTPUT_PATH

def __init__(self):
    self.config_file = 'selector_config.yml'

def get_extractor(self):
    return Extractor.from_yaml_file()


def extract_asin_data(self, html):
    extractor = self.get_extractor()
    return extractor.extract(html)

class UI:
    def __init__(self):
        self.page_url = "https://itdashboard.gov/"
        self.parent_xpath = "//div[@id='agency-tiles-container']//div[@class='tuck-5']/div[@class='row top-gutter-20']"
        self.agencies_data = None
        self.investments_data = None
        self.agency_title = "Department of Agriculture"
        self.browser_setup()

    def generate_excel(self):
        writer = pd.ExcelWriter(f"{OUTPUT_PATH}/{self.agency_title}.xlsx")
        self.agencies_data.to_excel(writer, sheet_name='Agencies')
        self.investments_data.to_excel(writer, sheet_name='Investments')

        # Close the Pandas Excel writer and output the Excel file.
        writer.save()

    def browser_setup(self):
        self.browser = Selenium()
        self.path_to_output = os.path.join(
            os.environ.get("ROBOT_ROOT", os.getcwd()), OUTPUT_PATH
        )
        preferences = {
            "download.default_directory": self.path_to_output,
            "plugins.always_open_pdf_externally": True,
            "download.directory_upgrade": True,
            "download.prompt_for_download": False,
        }
        self.browser.open_chrome_browser(self.page_url, preferences=preferences)

    def dive_in(self):
        com.wait_element(self.browser, "//a[@href='#home-dive-in']")
        self.browser.click_element_when_visible("//a[@href='#home-dive-in']")

    def get_agencies_data(self):
        com.wait_element(self.browser, self.parent_xpath)
        count = self.browser.get_element_count(self.parent_xpath)

        agencies = []
        for i in range(1, count + 1):
            title_xpath = f"({self.parent_xpath})[{i}]//span[1]"
            amount_xpath = f"({self.parent_xpath})[{i}]//span[2]"
            title = self.browser.get_text(title_xpath)
            amount = self.browser.get_text(amount_xpath)
            agencies.append({"Title": title, "Amount": amount})

        self.agencies_data = pd.DataFrame(agencies)

    def get_agency_detail(self):
        agency_button = f"{self.parent_xpath}//span[.='{self.agency_title}']/../../..//a[.='view']"
        com.wait_element(self.browser, agency_button)
        self.browser.click_element_when_visible(agency_button)

        select_xpath = "//select[@name='investments-table-object_length']"
        self.select_all(select_xpath)
        self.scrape_table()



    def select_all(self, xpath):
        com.wait_element(self.browser, xpath)
        self.browser.select_from_list_by_value(xpath, "-1")
        com.wait_element(self.browser, "//a[@class='paginate_button next disabled']")

    def scrape_table(self):
        table_raw_xpath = "//table[@id='investments-table-object']//tbody//tr"
        table_raw_count = self.browser.get_element_count(table_raw_xpath)
        self.get_pdf(table_raw_xpath)
        pdf_uii, pdf_inv_title = self.scrape_pdf()
        investments = []
        for i in range(1, table_raw_count + 1):
            uii = self.browser.get_text(f"({table_raw_xpath})[{i}]//td[1]")
            inv_title = self.browser.get_text(f"({table_raw_xpath})[{i}]//td[3]")
            investments.append(
                {
                    "UII": uii,
                    "Bureau": self.browser.get_text(f"({table_raw_xpath})[{i}]//td[2]"),
                    "Investment Title": inv_title,
                    "Total FY2021 Spending": self.browser.get_text(f"({table_raw_xpath})[{i}]//td[4]"),
                    "Type": self.browser.get_text(f"({table_raw_xpath})[{i}]//td[5]"),
                    "CIO Rating": self.browser.get_text(f"({table_raw_xpath})[{i}]//td[6]"),
                    "# of Projects": self.browser.get_text(f"({table_raw_xpath})[{i}]//td[6]"),
                    "PDF UII": pdf_uii if uii == pdf_uii else '',
                    "PDF Investment Title": pdf_inv_title if uii == pdf_uii else ''
                    "Compare UII": uii == pdf_uii if uii == pdf_uii else '',
                    "Compare Investment Title": inv_title == pdf_inv_title if uii == pdf_uii else ''
                }
            )
        self.investments_data = pd.DataFrame(investments)

    def get_pdf(self, table_xpath):
        # Open a new window
        pdf_xpath = f"{table_xpath}//td//a"
        pdf_url = self.browser.get_element_attribute(pdf_xpath, 'href')
        self.browser.execute_javascript("window.open('');")
        self.browser.switch_window("NEW")
        self.browser.go_to(pdf_url)
        button_xpath = "//div[@id='business-case-pdf']//a"
        com.wait_element(self.browser, button_xpath)
        self.browser.click_element_when_visible(button_xpath)
        import time
        time.sleep(10)
        self.browser.switch_window("MAIN")

    def scrape_pdf(self):
        parser = PDFParser(com.get_latest_file(f"{OUTPUT_PATH}/*"))
        investment = parser.get_by_key("Name of this Investment")
        uii = parser.get_by_key("Unique Investment Identifier")
        return (uii, investment)
