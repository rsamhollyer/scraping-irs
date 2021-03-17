import sys
import requests
from bs4 import BeautifulSoup as bs
import lxml
import json


def scrapeIRSPriorYearProducts(listOfForms):

    global results_list
    results_list = []
    index_off_first_row = 0
    results_per_page = 200
    # For the search results, need to have one value that is used as a check for the 2d list that is used for creating the .json() and the other is used as the search param on the website.

    for item in listOfForms:
        index_off_first_row = 0
        search_value = item
        search_value_url_param = search_value.replace(" ", "+")
        has_error_block = None

        while(has_error_block == None):
            url = f"https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage={results_per_page}&sortColumn=sortOrder&indexOfFirstRow={index_off_first_row}&criteria=formNumber&value={search_value_url_param}&isDescending=false"
            r = requests.get(url)
            soup = bs(r.text, 'lxml')

            # This is to stop the while loop
            error_block = soup.find(class_="errorBlock")
            has_error_block = error_block

            # Gets my scraped data in a single array [Form w2, desc, year, form w2, desc, year, ...etc]
            table_rows = [rows.text.strip() for rows in soup.find(
                class_="picklist-dataTable").find_all('td')]

            # The items belows are for creating a 2d list based on the table_rows list that groups by the left, center, and right column on the PY Products page
            # It also matches checks to see if a Product number does not match a form name and breaks the loop, to prevent non-asked for forms from appearing
            deep_list = []
            tmp = []

            for index in range(len(table_rows)):
                tmp.append(table_rows[index])

                if(tmp[0] != search_value):
                    break

                if(len(tmp) == 3):
                    deep_list.append(tmp)
                    tmp = []

            # I want to take my 2-dimensional list of returns and convert it all into a dictionary with the code below

            dict_list = []

            for items in deep_list:
                dict_list.append({
                    "form_number": items[0],
                    "form_title": items[1],
                    "min_year": items[2],
                    "max_year": items[2]
                })

                #  This is the final step, where I only want to return one json dictionary per search result and update the miniumum year as it iterates through the list `dict_list`

            for form in dict_list:
                if(len(results_list) == 0 or form['form_number'] != results_list[-1]['form_number']):
                    results_list.append(form)
                else:
                    results_list[-1]['min_year'] = form['min_year']

            index_off_first_row += results_per_page
    with open("data_file.json", "w") as f:
        json.dump(results_list, f)

    return results_list


# Uncomment to call the function with the example list below
# scrapeIRSPriorYearProducts(['Form 941', 'Form 1040', 'Publ 1', 'Publ 553', 'Form 941-C (PR)'])

# Use command line arguments to run the script, e.g.
# python search-irs-py-products.py 'Form 941' 'Form 1040' 'Publ 1' 'Publ 553' 'Form 941-C (PR)'
scrapeIRSPriorYearProducts(sys.argv[1:])
