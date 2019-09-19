# def find_by_year(b):
#     page_source=b.page_source
#     soup=bs4.BeautifulSoup(page_source, "lxml")
#     div_timeline=soup.find("div", attrs = {"class": "WB_timeline"})
#     soup_a_monthes=div_timeline.find_all("a", attrs = {"action-type": "select"})
#     list_monthes=[]
#     for soup_a_month in soup_a_monthes:
#         list_monthes.append(soup_a_month['action-data'])
#     a_years=b.find_elements(By.CSS_SELECTOR,'a[action-type="select_year"]')
#     for a_year in a_years:
#         print(a_year.text)
#         ActionChains(b).move_to_element(a_year).click(a_year).perform()
#         tmp_list=filter(lambda x: a_year.text in x, list_monthes)
#         wait(4)
#         for month in tmp_list:
#             pos_month= 'a[action-data="'+month+'"]'
#             a_month=b.find_element(By.CSS_SELECTOR,pos_month)
#             try:
#                 ActionChains(b).move_to_element(a_month).click(a_month).perform()
#                 wait(5)
#
#                 for i in range(10):
#                     b.execute_script("window.scrollTo(0, document.body.scrollHeight)");
#                     if is_element_exist(b,By.PARTIAL_LINK_TEXT, '下一页') is True:
#                         break
#                     wait(5)
#                 find_by_month(b)
#             except Exception as e:
#                 print(traceback.print_exc())
#
#     return 1