from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import pdb
import re
from lxml.html.diff import htmldiff

class SelObject(object):

    def __init__(self):
        self.useragent = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25"
        #profile = webdriver.PhantomJSProfile()
        #profile.set_preference("general.useragent.override",useragent)

        try:
	        self.br = webdriver.PhantomJS("./phantomjs")

	        #self.br = webdriver.Firefox()
        except Exception, e:
			print " [!] Browser object creation error:", e

        self.forms_and_inputs = {}
        self.links = []
        self.clicked_links = []
        self.last_url = ""
        self.base_url = ""

        self.last_response = ""
        self.last_html = ""
        self.reg_dict = {}
        self.temp_visited = []



	def __wait(self):
		time.sleep(2)

	def close(self):
		self.browser.close()

    def set_base_url(self,url):

        self.base_url = self.parse_malformed_url(url)

    def collect_link(self,url=""):
        index = 0
        if url == "":
            bsoup = self.parse_html_to_bs(self.last_html)
        else:
            self.temp_visited.append(url)
            if "logout" in url:
                return
            result = self.get_link(url)
            if result == False:
                return
            else:
                    bsoup = self.parse_html_to_bs(result)
        if bsoup != None:
            templinks = bsoup.findAll("a")
            self.get_input_attr(inputdata=templinks,key="href")
            templinks = [] 
            for pair in self.input_pairs:
                if (self.base_url.replace("http://","").replace("https://","") in pair["href"]) or (pair["href"].startswith("/")):
                    templinks.append(pair["href"])
                index += 1

            for link in templinks:
                if not self.base_url.endswith("/"):
                    tempurl = self.base_url+"/"
                else:
                    tempurl = self.base_url

                if link.startswith("http"):
                    new_link = link
                else:
                    new_link = tempurl+link
                if new_link not in self.links:
                    print "[*] discovered new link:"+new_link
                    self.links.append(new_link)

                if len(self.links)>= 10:
                    #print "[*] We have 10 links, thats enough"
                    return

    def parse_html_to_bs(self,data):
        try:
            temp_bs = bs([data],"lxml")
        except:
            return None 
        return temp_bs
    
    def collect_all_links(self, url=""):
        try:
            if self.links[0]:
                pass
        except:
            self.collect_link(url=url) 
        for link in self.links:
            if link not in self.temp_visited:
                print "[+] added link:"+link
                self.collect_link(link)

                self.temp_visited.append(link)
        if len(self.links)>=10:
            print "[*] We have 10 links, thats enough"
            return

    def get_reg(self, key):
        return self.reg_dict[key]

    
    def find_all_forms(self,url="",response=""):
        if response == "":
            bsoup = self.parse_html_to_bs(self.get_link(url=url))
        else:
            bsoup = response
        if bsoup != None:
            forms = bsoup.findAll("form")
            form_temp_list = []
            for form in forms:
                inner_temp_list = []
                inputs = form.findAll("input")
                buttons = form.findAll("button")
                inner_temp_list.append(form)
                for element in inputs:
                    inner_temp_list.append(element)
                for button in buttons:
                    inner_temp_list.append(button)
                form_temp_list.append(inner_temp_list)
                
            self.forms_and_inputs[self.parse_malformed_url(url)] = form_temp_list

    def parse_malformed_url(self,url):
            if url.startswith("127.0.0.1"):
                url = "http://"+url
            elif not url.startswith("http"):
                url = "http://"+url
            return url

    def inject_sql(self,url="",index=0, subtype=""):
        if url != "":
            if not self.forms_and_inputs[url]:
                print "No forms on the site %s"%(url)
                return
    
        with open("sqli.txt","r") as f:
            self.sqli_list = f.readlines()
        f.close()

        if url == "":
            tempurl = self.links[index]
        else:
            tempurl = url
        
        self.get_link(url=tempurl)
        if self.login_page in self.br.current_url():
            self.do_login("admin","password")
            self.get_link(url=tempurl)
        print "BROWSER_AFTER_LINK:"+str(self.br.current_url())

        for sqli in self.sqli_list:
            print "URL:"+tempurl
            print "SQLI:"+sqli
            self.submit_form_fields(payload=sqli, formindex=index,
                                    inputindex=0, subtype=subtype)

    def process_response(self,before_data,after_data, process_type = "injection", payloadpattern=""):
        diff_data = bs(str(htmldiff(after_data,before_data).split("<del>")[1:-1]))

        pdb.set_trace()

        if process_type == "injection":
            if re.search(r'[sS][qQ][lL]',diff_data.text):
                try:
                    print after_data.geturl()
                except:
                    pass
                #pdb.set_trace()

            if payloadpattern != "":
                if re.search(payloadpattern,after_data):
                    print "YESS YOU GOT IT"
                    pdb.set_trace()










    def check_login(self):

        if not self.forms_and_inputs:
            return 
        for element in self.forms_and_inputs[self.last_url][0][1:-1]:    
            if re.search(self.get_reg("login"),str(element)):
                try:
                    if self.forms_and_inputs[self.last_url][1]:
                        pass
                except:
                    self.login_page = self.br.geturl()
                    print self.login_page
                    return True
            
                logging.warning("Other forms to try")
                return False


    def do_login(self, username, password, authtype="form"):
        key = "name"
        if authtype=="form":
            if not self.login_page in self.br.geturl():
                self.get_link(self.login_page)
            self.br.select_form(nr=0)
            self.get_input_attr()
            for pair in self.input_pairs:
                if re.search(self.get_reg("user"),pair[key]):
                    self.br.form[pair[key]]=username
                if re.search(self.get_reg("password"),pair[key]):
                    self.br.form[pair[key]]=password

        self.last_response = self.br.submit()
        self.last_html = self.last_response.read()
        print self.cookies
        
    def submit_form_fields(self, payload="", formindex=0, inputindex=0, subtype=""):
        key = "name"
        self.get_input_attr(formindex=formindex)
        form = self.br.find_elements_by_tag_name[formindex]

        print "BROWSER_BEFORE_SUBMITTING:"+str(self.br.current_url())
        if subtype=="":
            print "INPUT_FIELD:"+str(self.input_pairs[inputindex][key])
            input_field = form.find_elements_by_tag_name([self.input_pairs[inputindex][key]])
            for field in input_field:
                field.send_keys(payload)

        temp_response_before = self.last_html
        form.submit()
        temp_response_after = self.br.page_source

        temp_result = self.process_response(temp_response_before,temp_response_after.read())

    def get_link(self,url,returntype="raw",response=""):

        url = self.parse_malformed_url(url)
        if not self.base_url:
            self.base_url = url
        self.last_url = url
        if "logout" in url: ### VERY IMPORTANT, BUT NEEDS ENHANCEMENT
            return False
        if response=="":
            try:
                self.br.get(url)
                self.last_html = self.br.page_source
            except URLError:
                try:
                    self.br.get(url.replace("http","https"))
                    self.last_html = self.br.page_source
                except:
                    pass
        else:
            self.last_response = response

        if returntype == "raw":
            return self.last_html


    def get_input_attr(self, inputdata="",key="name",formindex=0):
        self.input_pairs = []
        if inputdata=="":
            process_data = self.forms_and_inputs[self.last_url][formindex][1:-1]
        else:
            process_data = inputdata
        for inputfield in process_data:
            for attr in inputfield.attrs:
                if str(attr[0]) == key:
                    try:
                        self.input_pairs.append({key:str(attr[1])})
                    except:
                        pdb.set_trace()

        return self.input_pairs

    
    def modify_cookie(self, payload):

        self.cookies = self.br.get_cookies()

        cur_cookie = self.cookies[0]

        cookie_value = cur_cookie["value"]
        cur_cookie["value"] = cookie_value+payload

        self.br.add_cookie(cur_cookie)

        temp_data_before = self.last_html

        self.br.refresh()
        temp_data_after = self.br.page_source
        self.process_response(temp_data_before,temp_data_after,payloadpattern = payload)

    def execute_javascript(self,payload):
        val_payload = self.validate_javascript(payload)
        self.br.execute_script(val_payload)


    def validate_javascript(self,payload):
        return payload

    def print_forms(self):
        for link in self.links:
            self.find_all_forms(url = link)
        for key in self.forms_and_inputs.keys():
            print "++++++++++ "+key+" ++++++++++"+"\n\n"
            form_index = 0
            for form in self.forms_and_inputs[key]:
                print "[*] FORM"
                print form
                print "\n"
                print "[*] FORMFIELDS"
                for i in range(1,len(self.forms_and_inputs[key][form_index])):
                    print "[+]"+str(self.forms_and_inputs[key][form_index][i])
                print "\n\n"
                form_index += 1




selob = SelObject()

selob.find_all_forms("127.0.0.1/mutillidae/index.php?page=capture-data.php")
#selob.print_forms()
selob.modify_cookie("<script>document.getElementByTagName('body').innerHTML = ''</script>")

