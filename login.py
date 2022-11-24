from playwright.sync_api import sync_playwright
from time import sleep
from bs4 import BeautifulSoup

def waitClick(context, page, selector, type,  text='', handleNewPage=False):
    if handleNewPage:
        with context.expect_page() as new_page_info:
            ele = page.locator(selector = selector, has_text = text)

            ele = ele.nth(0)

            ele.wait_for()
            ele.click()

        new_page = new_page_info.value
        new_page.wait_for_load_state()

        return new_page

    else:
        if type == 'string':
            ele = page.locator(selector = selector, has_text = text)
        elif type == 'locator':
            ele = page.locator(selector = selector)


        ele = ele.nth(0)
            
        ele.wait_for()
        ele.click()

email = input("Insert your university email: ")
date = input("Insert the date of the recording (DD/MM/YYYY): ")

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)

    browser_context = browser.new_context(accept_downloads=True)
    browser_context.set_default_timeout(60000)

    page = browser_context.new_page()
    page.goto('http://polimi.it/servizionline')
    print(page.title())
    page.locator("asdas").count()
    waitClick(browser_context, page, '#srv_vm_514', 'locator')

    waitClick(browser_context, page, 'div.card', 'string', 'FONDAMENTI DI AUTOMATICA')

    waitClick(browser_context, page, '.section', 'string', 'Recordings')

    newPage = waitClick(browser_context, page, '.activity', 'string', 'Recordings archive', True)
    
    waitClick(browser_context, newPage, '.paginator_link', 'string', 'tutte')

    waitClick(browser_context, newPage, '.HeadColumn1', 'string', 'Data Registrazione')

    print(newPage.title())
    sleep(2)

    elements = newPage.locator('tbody.TableDati-tbody').inner_html()

    soup = BeautifulSoup(elements, features='html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        if date in row.text:
            videoLink = row.findChild('a', {'class': 'Link'})['href']

            videoLink = newPage.url.split('.it')[0] + '.it' + videoLink

            videoPage = browser_context.new_page()
            videoPage.goto(videoLink)
            videoPage.get_by_placeholder('Email address').fill(email)
            videoPage.get_by_text('Sign In').click()
            videoPage.locator('.ngPlayerWrapper').wait_for()
            input()

    browser.close()
