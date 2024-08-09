
/***********************************************************************************************\
 * Files needed:                                                                               *
 * httplib.h => https://github.com/yhirose/cpp-httplib                                         *
 * json.hpp  => https://github.com/nlohmann/json/blob/develop/single_include/nlohmann/json.hpp *
 * libcrypto-3-x64.dll                                                                         *
 * libssl-3-x64.dll                                                                            *
 * post_office.json                                                                            *
\***********************************************************************************************/


//#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
#define CPPHTTPLIB_OPENSSL_SUPPORT

#include <iostream>
#include <string>
#include <fstream>
#include <unordered_map>
#include <utility>
#include <codecvt>
#include <ctime>
#include "httplib.h"
#include "json.hpp"



#define API_KEY "AIzaSyDskLMtW6BvOlmjOBCScOs5rGknYbK3LcU"
#define REQ_DUR 1800 //unit: ��

#if (defined SAVE_SAVE_MONEY && defined SAVE_MONEY)

#undef SAVE_MONEY

#endif

using namespace std;

using json = nlohmann::json;
using dis_dur = pair<int, int>;

struct post_office
{
    int num;     //�l���N������(�Ʀr)
    string name; //�l���W��
    string loc;  //�l�� place id
    string zip_code; //�l���l���ϸ�
    unordered_map<string, dis_dur> info; //string: �l���N������(�Ʀr)   dis_dur(�Z��\�ɶ�)-> first: distance \ second: duration


};

wstring_convert<codecvt_utf8<wchar_t>> utf8;

class g_map {

public:

    g_map();

    //�s��l����T
    unordered_map<int, post_office> pfs;

    //��ƨ��o�ɶ�
    time_t rec_time;

    //�ɶ��榡�� Ex. 2024/08/08 13:00:00
    string rec_time_f;


private:

    //�s��google map api
    void g_map_connect();

    //�N��o���a�ϸ�T�g��json��
    void to_json(json js, fstream& out);

    //json to pfs
    void from_json();

    fstream in, out;
    json pf;
    bool error = false;
};

g_map::g_map() {

    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);

    //���J�l����T
    in.open("post_office.json", ios::in | ios::binary);

    if (!in.is_open()) {
        cout << R"(Can't open "post_offic.json")" << endl;
        system("pause");
        exit(EXIT_FAILURE);
    }

    in >> pf;
    in.close();

#if defined SAVE_MONEY
    //�P�_�O�_���W���Ķ���ƹL30 mins
    if (time(0) > (pf["time_stamp"] + REQ_DUR) || pf["time_stamp"] > time(0)) {
        g_map_connect();
    }
    else {
        from_json();
    }

#elif defined SAVE_SAVE_MONEY
    from_json();

#else
    g_map_connect();

#endif

    tm ttime;
    localtime_s(&ttime, &rec_time);
    char t_out[80] = { 0 };
    strftime(t_out, sizeof(t_out), "%Y/%m/%d %A %H:%M:%S\n", &ttime);

    rec_time_f = t_out;
}

void g_map::g_map_connect() {


    cout << "Connecting to Distance Matrix API..." << endl;
    httplib::Client cli("https://maps.googleapis.com");
    httplib::Params params;
    params.emplace("key", API_KEY);
    params.emplace("language", "zh_TW");

    json js;

    post_office* lpf = new post_office();
    for (int i = 0; i < pf["post_office"].size(); i++) {

        lpf->num = pf["post_office"][i]["index"];
        lpf->loc = pf["post_office"][i]["loc"];
        lpf->name = pf["post_office"][i]["name"];
        lpf->zip_code = pf["post_office"][i]["zip_code"];

        params.emplace("origins", lpf->loc);

        //��U�I�W��
        string des = "";

        //�p��Z��
        for (int j = 0; j < pf["post_office"].size(); j++) {

            if (j == i) continue;
            string tmp = "";
            pf["post_office"][j]["loc"].get_to(tmp);
            des += tmp + "|";
        }
        des.erase(des.end() - 1);

        //Connecting to Google API
        params.emplace("destinations", des);
        if (auto res = cli.Get("/maps/api/distancematrix/json", params, httplib::Headers())) {
            if (res->status == httplib::StatusCode::OK_200) {
                js = json::parse(res->body);

            }
        }
        else {
            auto err = res.error();
            std::cout << "HTTP error: " << httplib::to_string(err) << std::endl;
            exit(EXIT_FAILURE);
        }

        //Error handle
        if (js["status"] != "OK") {
            cerr << "Something went wrong, Error message: " << js["status"] << endl;
            error = true;
            break;
        }


        int index = 0;
        for (int j = 0; j < js["rows"][0]["elements"].size(); j++) {

            if (j == i)
                index++;
            lpf->info.insert(make_pair(to_string(index), make_pair(js["rows"][0]["elements"][j]["distance"]["value"], js["rows"][0]["elements"][j]["duration"]["value"])));
            index++;
        }


        pfs.insert(make_pair(i, *lpf));
        lpf->info.clear();
        params.erase("origins");
        params.erase("destinations");
    }
    delete lpf;

    out.open("post_office.json", ios::out | ios::binary);
    pf["time_stamp"] = (error == false) ? time(0) : 0;
    out << pf;
    out.close();
    rec_time = pf["time_stamp"];

    to_json(pf, out);

    if (error == true)
        exit(EXIT_FAILURE);

}

void g_map::to_json(json js, fstream& out) {

    for (int i = 0; i < pfs.size(); i++) {
        js["post_office"][i]["info"] = pfs[i].info;
    }

    out.open("post_office_with_info.json", ios::out);
    out << js;
    out.close();


}

void g_map::from_json() {

    fstream in;
    in.open("post_office_with_info.json", ios::in);
    if (!in.is_open()) {
        cout << R"(Can't open "post_office_with_info.json", connect to Distance Matrix API)" << endl;
        g_map_connect();
        return;
    }

    json pf;
    in >> pf;
    in.close();

    post_office* lpf = new post_office();
    for (int i = 0; i < pf["post_office"].size(); i++) {

        lpf->num = pf["post_office"][i]["index"];
        lpf->loc = pf["post_office"][i]["loc"];
        lpf->name = pf["post_office"][i]["name"];
        lpf->zip_code = pf["post_office"][i]["zip_code"];


        unordered_map<string, dis_dur> dd;
        pf["post_office"][i]["info"].get_to(dd);
        lpf->info = dd;

        pfs.insert(make_pair(i, *lpf));
        lpf->info.clear();
    }
    delete lpf;
    rec_time = pf["time_stamp"];
}


ostream& operator<<(ostream& os, const g_map& gm) {

    cout << utf8.to_bytes(L"��ƨ��o�ɶ�: ") << gm.rec_time_f << endl;

    for (auto x : gm.pfs) {
        cout << "Start: " << x.second.name << endl;
        for (auto w : x.second.info)
            cout << gm.pfs.find(stoi(w.first))->second.name << ": " << w.second.first << utf8.to_bytes(L" ����") << " Time: " << w.second.second << " s" << endl;
        cout << "------------------------------------------" << endl;
    }

    return os;
}