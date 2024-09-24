﻿
#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
#define SAVE_MONEY
//#define SAVE_SAVE_MONEY
//#define PROOF
#define SA

#include <iostream>
#include <random>
#include <vector>
#include <algorithm>
#include <iomanip>
#include "google_map.hpp"

#define T0 1e6        //初始溫度
#define iter 250      //迭代次數
#define TRY_MAX 1.8e5 //嘗試次數最大值


using namespace std;

string color(int c)
{
    int r = c >> 16;
    int g = (c & 0xFF00) >> 8;
    int b = c & 0xFF;
    string s = "\033[38;2;" + to_string(r) + ";" + to_string(g) + ";" + to_string(b) + "m";
    return s;
}

void loading(size_t process, size_t total, string s = "") {

    int count = 0;
    int color_p[20] = { 0xFCE3D0, 0xFCDDC6, 0xFBD8BD, 0xFBD2B3, 0xFACCAA,
                        0xFAC7A0, 0xF9C197, 0xF8BB8E, 0xF8B684, 0xF7B07B,
                        0xF7AA71, 0xF6A568, 0xF69F5E, 0xF59A55, 0xF5944B,
                        0xF48E42, 0xF38939, 0xF3832F, 0xF27D26, 0xF2781C };
    cout << "\r" << "\033[?25l";

    printf("%s %llu / %llu => %llu%% [", s.c_str(), process, total, size_t(process * 100.0 / total));
    for (int j = 5; j <= int(process * 100.0 / total); j += 5)
    {
        cout << "\033[0m" << color(color_p[count]) << "##" << "\033[0m";
        count++;
    }
    for (int i = count; i <= 19; i++)
    {
        cout << "..";
    }
    count = 0;
    cout << "]";
}


int main()
{
    //創建g_map類別從google獲取距離資料
    g_map gm;
    unordered_map<int, post_office> pfs = gm.pfs;

    //用來產生隨機數
    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<double> nd(0.0, 1.0); //隨機數變為均勻分佈(0~1)

    vector<int> pf_vec; //郵局順序
    vector<int> shortest_vec; //郵局最短順序
    int s_dis = 1e9; //移動的最短距離
    int start = 0; //起始與終點郵局

    cout << utf8.to_bytes(L"資料取得時間: ") << gm.rec_time_f << endl;

    for (int i = 0; i < pfs.size(); i++) {

        if (i != 0 && i % 6 == 0)
            cout << endl << endl;

        cout << "[" << pfs[i].num << "] " << pfs[i].name << " ";
    }
    cout << endl << endl << utf8.to_bytes(L"輸入起點郵局(代碼): ");
    cin >> start;
    while (!(start >= 0 && start < pfs.size())) {

        cout << endl << utf8.to_bytes(L"輸入範圍錯誤，請重新輸入: ");
        cin >> start;
    }
    cout << endl;

    //建立郵局順序vector
    pf_vec.push_back(start);
    for (int i = 0; i < pfs.size(); i++) { //更改 pfs.size() 可以更改測試個數　
        if (i == start)
            continue;
        pf_vec.push_back(i);
    }
    pf_vec.push_back(start);

    vector<int> now_vec = pf_vec;

#ifdef SA
    double y = 0;
    double t0 = T0;

    //嘗試次數
    int try_cnt = 1;

    for (int i = 0; i < iter; i++) {

        if (try_cnt > TRY_MAX) {
            cout << endl << "Have tried " << TRY_MAX << " times!!!!" << endl;
            break;
        }

        int l_dis = 0;

        //計算這個組合距離總長
        for (int j = 0; j < now_vec.size() - 1; j++) {

            //先找對應node，再找對下一個node的距離 info.first->distance info.second->duration time
            l_dis = l_dis + pfs[now_vec[j]].info[to_string(now_vec[j + 1])].first;
        }

        //y是由結果產生的0~1的值， 之後要擲骰子確定是否要留下結果
        if (l_dis < s_dis)
            y = 1;
        else
            y = 1 / exp((l_dis - s_dis) / t0);

        //x是0~1隨機數，若y > x則採用組合，反之則否
        double x = nd(gen);

        // 接受結果
        if (y > x) {
            shortest_vec = now_vec;
            s_dis = l_dis;


            cout << "\r\033[38;2;235;118;65m" << utf8.to_bytes(L"迭代次數: ") << i << " Temp: ";
            printf("%.3f                                                                       \033[0m\n", t0);
            cout << "Now: ";
            for (auto x : now_vec)
                cout << x << " ";
            cout << "  " << "Shortest: ";
            for (auto w : shortest_vec)
                cout << w << " ";
            cout << " Dis: " << s_dis << endl;
            cout << "==============================================================================================================" << endl;


            //降溫
            t0 = t0 * 0.9;

            //嘗試次數變回0
            try_cnt = 0;

        }

        // 不接受結果
        else {
            i--;

            loading(try_cnt, TRY_MAX, "Trying, please wait...");
            try_cnt++;

        }
        //遊歷路徑重新組合
        shuffle(now_vec.begin() + 1, now_vec.end() - 1, gen);

    }

    cout << endl;
    cout << "Shortest Distance: " << s_dis << endl;
    cout << "Path:" << endl;
    for (auto it = shortest_vec.begin(); it != shortest_vec.end(); it++) {

        if (it == shortest_vec.begin())
            cout << pfs[*it].name;
        else
            cout << " -> " << pfs[*it].name;
    }
    cout << endl << endl;
#endif 

#ifdef PROOF
    //驗證
    size_t total = 1;
    for (int i = 1; i <= pfs.size() - 1; i++) {

        total = total * i;

    }

    now_vec = pf_vec;
    s_dis = 1e8;
    shortest_vec = now_vec;
    int t = 1;
    sort(now_vec.begin() + 1, now_vec.end() - 1);

    cout << "Finding Best Solution" << endl;

    do {

        int l_dis = 0;

        //計算這個組合距離總長
        for (int j = 0; j < now_vec.size() - 1; j++) {

            //先找對應node，再找對下一個node的距離 info.first->distance info.second->duration time
            l_dis = l_dis + pfs[now_vec[j]].info[to_string(now_vec[j + 1])].first;
        }

        if (l_dis < s_dis) {

            s_dis = l_dis;
            shortest_vec = now_vec;

        }
        loading(t, total);

        /*cout << "\033[38;2;174;239;121m" << utf8.to_bytes(L"組合次數: ");
        printf("%d\033[0m\n", t);
        cout << "Now: ";
        for (auto x : now_vec)
            cout << x << " ";
        cout << "  " << "Shortest: ";
        for (auto w : shortest_vec)
            cout << w << " ";
        cout << " Dis: " << l_dis << endl;
        cout << "---------------------------------------------------------------------" << endl;*/

        t++;
    } while (next_permutation(now_vec.begin() + 1, now_vec.end() - 1));
    cout << endl;
    cout << "Shortest Distance: " << s_dis << endl;
    cout << "Path:" << endl;
    for (auto it = shortest_vec.begin(); it != shortest_vec.end(); it++) {

        if (it == shortest_vec.begin())
            cout << pfs[*it].name;
        else
            cout << " -> " << pfs[*it].name;
    }
    cout << endl;
#endif

    return 0;
}

