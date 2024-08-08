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
    {
        "index": 0,
        "loc": "place_id:ChIJb2HleAc1aDQRNgCqh8u6PU4",
        "name": "新竹武昌街郵局",
        "zip_code": "300191"
    }

```

        

