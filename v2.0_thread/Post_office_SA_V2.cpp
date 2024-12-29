#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING

//#define PROOF
//#define SA

#include <iostream>
#include <random>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <thread>
#include <chrono>
#include <mutex>
#include <algorithm>
#include "google_map.hpp"

#define T0 1e6        //初始溫度
#define iter 250      //迭代次數
#define TRY_MAX 1.8e5 //嘗試次數最大值
#define Threads_cnt 20     //執行緒數量

int done_cnt = Threads_cnt;
bool done = false;
std::mutex mtx;

using namespace std;

struct message {
    string msg1 = "";
    string msg2 = "";
    int time_cost = 0;
    vector<int> s_r;

};

vector<message> t_vec(Threads_cnt);

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

time_t get_time(string s) {

    struct tm t = { 0 };
    int hour, min, sec;
    sscanf_s(s.c_str(), "%d:%d:%d", &hour, &min, &sec);
    t.tm_year = 2024 - 1900;
    t.tm_mon = 9 - 1;
    t.tm_mday = 11;
    t.tm_hour = hour;
    t.tm_min = min;
    t.tm_sec = sec;
    return mktime(&t);
}

void show_time(time_t t) {

    struct tm ttime;
    localtime_s(&ttime, &t);
    char t_out[80] = { 0 };
    strftime(t_out, sizeof(t_out), "%Y/%m/%d %A %H:%M:%S\n", &ttime);
    cout << t_out;

}

void print() {
    while (true)
    {
        for (int i = 0; i < Threads_cnt; i++)
        {
            cout << "ID: " << i << endl;
            cout << "\r" << t_vec[i].msg1 << "                          " << endl;
            cout << "\r" << t_vec[i].msg2 << "      " << endl;
            if (i != Threads_cnt - 1)
                cout << "==============================================================================================================" << endl;

        }
        int up = Threads_cnt * 3 + Threads_cnt - 1;
        printf("\033[%dA", up);
        if (done == true) {
            break;
        }
    }

}


void SA(time_t now, int start, int idd) {

    g_map gm;

    double y = 0;
    double t0 = T0;
    unordered_map<int, post_office> pfs;
    time_t now_t = now;
    tm ttime;


    //嘗試次數
    int try_cnt = 1;
    int stay_time;

    localtime_s(&ttime, &now);
    int start_hour = ttime.tm_hour;
    int now_hour = ttime.tm_hour;

    vector<unordered_map<int, post_office>> pfs_v;

    //創建g_map類別從google獲取距離資料

    for (int i = 0; i < 4; i++) {

        if (ttime.tm_hour + i > 16)
            break;
        string num = to_string(ttime.tm_hour + i);
        string fn = "data\\post_office_with_info_" + num + ".json";
        gm.from_json(fn);
        unordered_map<int, post_office> pfs = gm.pfs;
        pfs_v.push_back(pfs);
        //cout << gm << endl;
    }

    pfs = pfs_v[0];

    //用來產生隨機數
    random_device rd;
    int seed = rd();
    //cout << "Seed: " << seed << endl;
    mt19937 gen(seed);
    uniform_real_distribution <double> nd(0.0, 1.0); //隨機數變為均勻分佈(0~1)
    uniform_int_distribution<> id(1, pfs.size() - 1);
    uniform_int_distribution<> st(1, 20);

    vector<int> pf_vec; //郵局順序
    vector<int> shortest_vec; //郵局最短順序
    int s_time_cs = 1e9; //移動的最短距離



    //建立郵局順序vector
    pf_vec.push_back(start);
    for (int i = 0; i < pfs.size(); i++) { //更改 pfs.size() 可以更改測試個數　
        if (i == start)
            continue;
        pf_vec.push_back(i);
    }
    pf_vec.push_back(start);

    vector<int> now_vec = pf_vec;
    string Msg1 = "";
    string Msg2 = "";

    for (int i = 0; i < iter; i++) {

        if (try_cnt > TRY_MAX) {


            break;
        }

        if (t0 < 1e-2) {

            break;
        }

        int l_time_cs = 0;

        //計算這個組合距離總長
        for (int j = 0; j < now_vec.size() - 1; j++) {

            //先找對應node，再找對下一個node的距離 info.first->distance info.second->duration time
            l_time_cs = l_time_cs + pfs[now_vec[j]].info[to_string(now_vec[j + 1])].second;
            //停留時間(秒)
            stay_time = 0;
            //現在時間
            now_t = now_t + pfs[now_vec[j]].info[to_string(now_vec[j + 1])].second + stay_time;
            //show_time(now_t);

            localtime_s(&ttime, &now_t);
            if (ttime.tm_hour > now_hour && ttime.tm_hour <= 16) {

                pfs = pfs_v[ttime.tm_hour - start_hour];
                now_hour = ttime.tm_hour;
            }
        }
        now_t = now;

        //y是由結果產生的0~1的值， 之後要擲骰子確定是否要留下結果
        if (l_time_cs < s_time_cs)
            y = 1;
        else
            y = 1 / exp((l_time_cs - s_time_cs) / t0);

        //x是0~1隨機數，若y > x則採用組合，反之則否
        double x = nd(gen);

        // 接受結果
        if (y > x) {
            shortest_vec = now_vec;
            s_time_cs = l_time_cs;

            Msg1 = utf8.to_bytes(L"迭代次數: ") + to_string(i) + " Temp: ";
            char tmp_c[80];
            sprintf_s(tmp_c, "%.2f", t0);
            Msg1 += tmp_c;

            t_vec[idd].s_r = shortest_vec;
            t_vec[idd].time_cost = s_time_cs;

            Msg1 += " Now: ";
            for (auto x : now_vec) {

                Msg1 += to_string(x) + " ";

            }
            Msg1 += "Time cost: " + to_string(s_time_cs);

            //降溫
            t0 = t0 * 0.9;

            //嘗試次數變回0
            try_cnt = 0;

        }

        // 不接受結果
        else {
            i--;
            now_vec = shortest_vec;
            Msg2 = "Trying, please wait " + to_string(try_cnt) + "/" + to_string(int(TRY_MAX)) + " " + to_string(int(float(try_cnt * 100) / float(TRY_MAX))) + "%      ";

            try_cnt++;

        }
        //遊歷路徑重新組合
        shuffle(now_vec.begin() + 1, now_vec.end() - 1, gen);
        /*int first = id(gen);
        int second = id(gen);
        while (first == second) {
            second = id(gen);
        }
        swap(now_vec[first], now_vec[second]);*/
        t_vec[idd].msg1 = Msg1;
        t_vec[idd].msg2 = Msg2;
    }

    t_vec[idd].msg1 = "\033[38;2;65;211;31m" + Msg1 + "\033[0m";

    mtx.lock();
    done_cnt--;
    mtx.unlock();

}

int main()
{
    g_map gm;
    time_t now;
    int stay_time = 0;

    cout << utf8.to_bytes(L"歡迎使用郵局最短路徑計算程式") << endl << utf8.to_bytes(L"輸入起始時間 (ex. 12:03:04 或 -1 即現在時間 ps.資料由 AM 9:00 to PM 5:00): ");
    string s;
    cin >> s;
    tm ttime;

    if (s == "-1") {
        now = time(0);
        localtime_s(&ttime, &now);
        while (ttime.tm_hour < 9 || ttime.tm_hour > 16) {
            cout << utf8.to_bytes(L"輸入時間範圍錯誤，請重新輸入: ");
            cin >> s;
            if (s == "-1")
                now = time(0);
            else
                now = get_time(s);
            localtime_s(&ttime, &now);
        }

    }
    else {
        now = get_time(s);
        localtime_s(&ttime, &now);
        while (ttime.tm_hour < 9 || ttime.tm_hour > 16) {
            cout << utf8.to_bytes(L"輸入時間範圍錯誤，請重新輸入: ");
            cin >> s;
            if (s == "-1")
                now = time(0);
            else
                now = get_time(s);
            localtime_s(&ttime, &now);
        }

    }

    time_t now_t = now;
    int start;


    string fn = "data\\post_office_with_info_9.json";
    gm.from_json(fn);
    unordered_map<int, post_office> pfs = gm.pfs;

    cout << utf8.to_bytes(L"開始時間: ");
    printf("%02d:%02d:%02d\n", ttime.tm_hour, ttime.tm_min, ttime.tm_sec);

    for (int i = 0; i < 14; i++) {

        if (i != 0 && i % 6 == 0)
            cout << endl << endl;

        cout << "[" << pfs[i].num << "] " << pfs[i].name << " ";
    }
    cout << endl << endl << utf8.to_bytes(L"輸入起點郵局(代碼): ");
    cin >> start;
    while (!(start >= 0 && start < 14)) {

        cout << endl << utf8.to_bytes(L"輸入範圍錯誤，請重新輸入: ");
        cin >> start;
    }
    cout << endl;

    vector<thread> threads;
    auto eval_start = chrono::steady_clock::now();
    for (int i = 0; i < Threads_cnt; i++) {
        threads.push_back(thread(SA, now, start, i));
        threads[i].detach();
    }
    cout << "\033[?25l";

    thread tp(print);
    tp.detach();
    while (done_cnt > 0) {

    }
    auto eval_end = chrono::steady_clock::now();
    auto duration = chrono::duration_cast<chrono::seconds>(eval_end - eval_start);

    this_thread::sleep_for(chrono::milliseconds(1));
    done = true;
    this_thread::sleep_for(chrono::milliseconds(1));
    printf("\033[%dB\033[0m", Threads_cnt * 3 + Threads_cnt);

    sort(t_vec.begin(), t_vec.end(), [](message a, message b) {return a.time_cost < b.time_cost; });
    int s_time_cs = t_vec[0].time_cost;
    vector<int> shortest_vec = t_vec[0].s_r;

    cout << endl;
    cout << "Shortest Distance: " << s_time_cs << endl;
    cout << "Path:" << endl;
    for (auto it = shortest_vec.begin(); it != shortest_vec.end(); it++) {

        if (it == shortest_vec.begin())
            cout << pfs[*it].name;
        else
            cout << " -> " << pfs[*it].name;
    }
    cout << endl;
    printf("Benchmark = %d x %d = %d\n", s_time_cs, duration.count(), s_time_cs * duration.count());
    cout << "\033[?25h";

    return 0;
}