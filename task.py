import os
import time
from libraries import common as com
from libraries.ui import UI

def main():
    """
    Main function which calls all other functions.
    """
    dashboard = UI()
    dashboard.dive_in()
    dashboard.get_agencies_data()
    dashboard.get_agency_detail()
    dashboard.generate_excel()
    # time.sleep(10)

if __name__ == "__main__":
    main()
