import sys
import requests
from bs4 import BeautifulSoup as bs
import lxml
import os


def printIRSForms(form, years_list):
    index_off_first_row = 0
    results_per_page = 25
    search_value = form
    search_value_url_param = search_value.replace(" ", "+")

    url = f"https://apps.irs.gov/app/picklist/list/priorFormPublication.html?resultsPerPage={results_per_page}&sortColumn=sortOrder&indexOfFirstRow={index_off_first_row}&criteria=formNumber&value={search_value_url_param}&isDescending=false"
    r = requests.get(url)
    soup = bs(r.text, 'lxml')

    table = soup.find('table', class_='picklist-dataTable')
    cols = [col for col in table.find_all(
        class_="LeftCellSpacer") if col.text.strip() == search_value]

    links = []

    for col in cols:
        link = col.find('a')['href']
        links.append(link)

    for link in links:
        for year in years_list:
            if year in link:
                filename = f"./{search_value}/{search_value}-{year}.pdf"
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, 'wb') as f:
                    f.write(requests.get(link).content)

# Uncomment to call the function with the example arguments below
# printIRSForms("Form 941", ["2020", "2019"])
# printIRSForms("Form 1040", ["2020", "2019", "2018", "2017", "2016"])


# Use command line arguments to run the script, e.g.
# python print-irs-form.py 'Form 941' 2020 2019
command_line_args = sys.argv
printIRSForms(command_line_args[1], command_line_args[2:])
