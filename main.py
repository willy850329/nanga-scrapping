from nanga import *

result = []
url_list_file = "url_list.txt"
url_list = get_url_list(url_list_file)
driver = get_driver()
for idx, url in enumerate(url_list):
    print("******************************************************************")
    print("item #"+str(idx)+" processing")
    result.append(get_meta_data(driver,url))
    print("Done!!")
df = pd.DataFrame(result, columns=['商品名', '商品連結', '顏色', '尺寸', '商品介紹','商品規格','日本官網售價'])
df.to_csv("out.csv", index=False)