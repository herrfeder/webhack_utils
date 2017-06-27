from wh_framework_sel import SelObject

url = "127.0.0.1/mutillidae"
#url = "127.0.0.1/dvwa"

selob = SelObject()
selob.find_all_forms(url)
selob.collect_all_links(url)
if (selob.check_login()):
    selob.do_login("admin","password")
selob.collect_all_links(url)

for link in selob.links:
    selob.find_all_forms(link)
selob.print_forms()
#selob.modify_cookie("<script>document.getElementByTagName('body').innerHTML = ''</script>")

