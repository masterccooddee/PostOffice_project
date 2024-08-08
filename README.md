# 必備檔案
+ [httplib.h](https://github.com/yhirose/cpp-httplib)
+ [json.hpp](https://github.com/nlohmann/json/blob/develop/single_include/nlohmann/json.hpp)
+ google_map.hpp
+ libcrypto-3-x64.dll
+ libssl-3-x64.dll 
+ post_office.json


> [!IMPORTANT]
> 本次project使用到Google的***Distance Matrix API***，與Google API傳送請求需要OpenSSL，因此請參閱[下載OpenSSL for Win](https://blog.csdn.net/m0_46665077/article/details/125609435)與[OpenSSL VS 配置教學](https://blog.csdn.net/m0_51531114/article/details/132207881) (若依照教學在lib的配置中需包含資料夾到MD)
>
>![](image/MD.png)


# 操作指南

## google_map.hpp
>[!IMPORTANT]
>需搭配 ***post_office.json*** 使用

### *post_office.json*
裡面有以下內容：

```json
"post_office":[
{
    "index": 0,
    "loc": "place_id:ChIJb2HleAc1aDQRNgCqh8u6PU4",
    "name": "新竹武昌街郵局",
    "zip_code": "300191"
}
],
"time_stamp":1723097571
```
+ `index`:    代表郵局編號
+ `loc`:      郵局的 place id
+ `name`:     郵局的名稱
+ `zip_code`: 郵遞區號 
+ `time_stamp`: 取得資料的時間 (unix timestamp)


裡面的郵局資料都能繼續增加，用以上格式填寫，**`index`**需照順序填寫
>[!NOTE]
>現有的資料中包含新竹市東區所有郵局
>
>參照：[新竹市當地支局](https://subservices.post.gov.tw/post/internet/Q_localpost/index.jsp?ID=12070201&search_area=%E6%96%B0%E7%AB%B9%E5%B8%82&desc=lp004_06.htm#list)
        

