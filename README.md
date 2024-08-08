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


裡面的郵局資料都能繼續增加，用以上格式填寫，`index`需照順序填寫
>[!NOTE]
>現有的資料中包含新竹市東區所有郵局
>
>參見：[新竹市當地支局](https://subservices.post.gov.tw/post/internet/Q_localpost/index.jsp?ID=12070201&search_area=%E6%96%B0%E7%AB%B9%E5%B8%82&desc=lp004_06.htm#list)

### *post_office_with_info.json*
比 *post_office.json* 多了 info 資訊，巨集[`SAVE_MONEY`](#SAVE_MONEY)與[`SAVE_SAVE_MONEY`](#SAVE_SAVE_MONEY)會用到

### *google_map.hpp*
>[!IMPORTANT]
>需搭配 ***post_office.json*** 使用

class g_map為其核心
```cpp
class g_map {

public:
    
    g_map();

    //存放郵局資訊
    unordered_map<int, post_office> pfs;
    //資料取得時間
    time_t rec_time;
    //時間格式化 Ex. 2024/08/08 13:00:00
    string rec_time_f;

private:

    //連接google map api
    void g_map_connect();
    //將獲得的地圖資訊寫成json檔
    void to_json(json js, fstream& out);
    //json to pfs
    void from_json();

    fstream in, out;
    json pf;
    bool error = false;
};
```
