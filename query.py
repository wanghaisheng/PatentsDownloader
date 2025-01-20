# -*- coding: utf-8 -*-
"""
  
"""

import webbrowser
import os
import time
import urllib.parse
import re
import logging
from config import * # note this will load local config.py file
from patentdetail import get_pantent_info
from patentdown import get_pantent_pdf, download_all_patents, DIR_PATH, check_local_patent
from utils import open_search_page, validate_patent_number, print_menu


# Configure logging
logging.basicConfig(
    filename='patent_download.log',  # Log file name
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)


def main_menu():
    """
    主菜单函数，提供用户选择关键词查询、专利号直接下载或退出程序的选项。
    Modified to read configuration from environment variables or defaults, and skips user input
    """
    logging.info("Starting script")

    # Get configuration from environment variables with defaults
    mode = os.getenv('PATENT_DOWNLOAD_MODE', 'keyword').lower()  # 'keyword' or 'direct'
    keywords = os.getenv('PATENT_KEYWORDS', '无人机')
    patent_no = os.getenv('PATENT_NUMBER', '')
    logging.info(f"Mode: {mode}, Keywords: {keywords}, Patent Number: {patent_no}")
    
    if mode == 'keyword':
       if not keywords:
           logging.error("PATENT_KEYWORDS environment variable is not defined. Exit the program")
           return
       keyword_search_menu(keywords)
    elif mode == 'direct':
        if not patent_no:
           logging.error("PATENT_NUMBER environment variable is not defined. Exit the program")
           return
        direct_download_menu(patent_no)
    else:
        logging.error("Invalid PATENT_DOWNLOAD_MODE environment variable. Use 'keyword' or 'direct'. Exit the program")

    logging.info("Script finished")


def keyword_search_menu(keywords):
    """
    关键词查询菜单函数，允许用户输入关键词进行专利查询，并提供下载选项.
    Modified to accept keyword as parameter
    """
    logging.info(f"Starting keyword search for: {keywords}")

    open_search_page(keywords)
    current_page = 1

    while True:
        patents = get_pantent_info(keywords, current_page)
        logging.info(f"  Current keyword: {keywords}, Page: {current_page}")
        logging.info(f"  Current patent list:")
        for i, patent in enumerate(patents, 1):
            logging.info(f"    {i}. {patent['专利号']} - {patent['标题']}")

        if not patents:
            logging.info("  No patents found, go back to main menu")
            break


        options = {
            "0": "下载所有专利",
            "1-N": "下载对应编号的专利",
            "X": "下一页",
            "S": "上一页",
            "R": "返回关键词搜索",
            "M": "返回主菜单",
            "Q": "退出程序"
        }
        print_menu("选项", options) # printing the menu might not be necessary when using in environment variables

        # Simplified download logic, since we don't need menu anymore
        choice = os.getenv('PATENT_KEYWORD_MENU_CHOICE', '0')
        logging.info(f"  Menu choice: {choice}")

        if choice == '0':
           successful, failed = download_all_patents(keywords)
           logging.info(f"  Batch download complete, success: {successful}, failed: {failed}")
           break
        elif choice.isdigit() and 1 <= int(choice) <= len(patents):
            patent = patents[int(choice) - 1]
            local_file = check_local_patent(patent['专利号'])
            if local_file:
                logging.info(f"  Patent file already exists: {local_file}")
            else:
                try:
                   get_pantent_pdf(patent['专利号'])
                   logging.info(f"  Finished download, : {patent['标题']} ({patent['专利号']})")
                except Exception as e:
                   logging.error(f"  Download failed: {patent['标题']} ({patent['专利号']}). Error: {str(e)}")
            break
        elif choice == 'X':
           current_page += 1
        elif choice == 'S':
           if current_page > 1:
                current_page -= 1
           else:
                logging.info("  Already on first page")
        elif choice == 'R':
            break
        elif choice == 'M':
           return
        elif choice == 'Q':
            logging.info("Exiting program")
            exit()
        else:
            logging.warning("  Invalid choice, please check PATENT_KEYWORD_MENU_CHOICE")
            break



def direct_download_menu(patent_no):
    """
    直接下载菜单函数，允许用户输入专利号进行下载，并检查本地是否已存在该专利文件.
    Modified to accept patent_no as parameter
    """
    logging.info(f"Starting direct download for patent number: {patent_no}")

    validation_result = validate_patent_number(patent_no)
    if validation_result is True:
        local_file = check_local_patent(patent_no)
        if local_file:
            logging.info(f"  Patent file already exists: {local_file}")
        else:
            if get_pantent_pdf(patent_no):
                logging.info(f"  Finished downloading patent: {patent_no}")
            else:
                logging.info(f"  Failed to download patent: {patent_no}")
    else:
        logging.error(f"Patent number format is incorrect: {validation_result}")


if __name__ == "__main__":
    main_menu()
