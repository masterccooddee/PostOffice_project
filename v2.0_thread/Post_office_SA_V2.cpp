#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING

//#define PROOF
#define SA

#include <iostream>
#include <random>
#include <vector>
#include <algorithm>
#include <iomanip>
#include "google_map.hpp"
#include <thread>

#include <mutex>

mutex mtx;
int counter = 0;

#define T0 1e6        //初始溫度
#define iter 250      //迭代次數
#define TRY_MAX 2e4 //嘗試次數最大值
#define thread_num 1  //執行緒數量


using namespace std;

//vector<unordered_map<int, post_office>> pfs_v;
//unordered_map<int, post_office> pfs;
//vector<int> pf_vec; //郵局順序
//vector<int> now_vec;
//vector<int> shortest_vec; //郵局最短順序
uniform_real_distribution <double> nd(0.0, 1.0); //隨機數變為均勻分佈(0~1)

tm ttime;
time_t nowtime;
time_t now;
int start_hour;
int now_hour;
int s_time_cs = 1e9; //移動的最短距離
int start = 0; //起始與終點郵局
int stay_time = 0;
//int* iter_now = new int();

int shared_counter = thread_num;
random_device rd;
bool finish = false;


int seed[thread_num];

//array<mt19937, 2> gen = { mt19937(seed1), mt19937(seed2) };

struct info
{
  vector <int> now_vec;
  string message1;
  string message2;
};

vector <info> *print_message;

struct ddata
{
  int now_hour;
  int s_time_cs; //移動的最短距離
  time_t now_t;
  vector<unordered_map<int, post_office>> pfs_v;
  unordered_map<int, post_office> pfs;
  //vector<int> pf_vec; //郵局順序
  vector<int> now_vec;
  vector<int> shortest_vec; //郵局最短順序
  uniform_int_distribution<> id_rand;
  mt19937 gen;
};

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


void Printout() {
  int i,up;
  int lineCounter = 0;
  this_thread::sleep_for(chrono::milliseconds(300));
  while(shared_counter != 0)
  {   
    for (i = 0; i < thread_num; i++)
    {
      if (lineCounter >= 5)
      {
        printf("\033[s\033[%dB\033[u", 20);
        lineCounter = 0;
      }
	  cout << "ThreadID : " << i << endl;
      cout << (*print_message)[i].message1 << endl;
      cout << (*print_message)[i].message2 << endl;
      if (i != thread_num - 1)
      {
        printf("\033[38;2;235;118;65m+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\033[0m\n");
      }
      lineCounter += 4;

    }
    up = thread_num * 3 + thread_num - 1;
    printf("\033[%dA", up);
  }
  if (finish == true)
  {
    return;
  }
}


void SA_test(ddata* one, int id)
{
  //vector<int> shortest_vec; //郵局最短順序
  
  double y = 0;
  double t0 = T0;

  //嘗試次數
  int try_cnt = 1;
  //thread::id id = this_thread::get_id();
  //cout << "Thread " << id << "started" <<  std::endl <<endl;
  //this_thread::sleep_for(chrono::milliseconds(100));
  
  for (int i = 0; i < iter; i++) 
  {
    //*iter_now = i;
    /*mutex mtx;
    mtx.lock();
    Printout(one,i);
    mtx.unlock();*/
    if (try_cnt > TRY_MAX) {
      //cout << endl << "Have tried " << TRY_MAX << " times!!!!" << endl;
	  (*print_message)[id].message1 = "Have tried " + to_string(TRY_MAX) + " times!!!!";
	  (*print_message)[id].message2 = "End";
      break;
    }

    if (t0 < 1e-2) {
      //cout << "Temperature is under 1e-8!!!" << endl;
	  (*print_message)[id].message1 = "Temperature is under 1e-8!!!";
      (*print_message)[id].message2 = "End";
      break;
    }

    int l_time_cs = 0;

    //計算這個組合距離總長
    for (int j = 0; j < one->now_vec.size() - 1; j++) {

      //先找對應node，再找對下一個node的距離 info.first->distance info.second->duration time
      l_time_cs = l_time_cs + one->pfs[one->now_vec[j]].info[to_string(one->now_vec[j + 1])].second;
      //停留時間(秒)
      stay_time = 0;
      //現在時間
      one->now_t = one->now_t + one->pfs[one->now_vec[j]].info[to_string(one->now_vec[j + 1])].second + stay_time;
      //show_time(now_t);

      localtime_s(&ttime, &one->now_t);
      if (ttime.tm_hour > one->now_hour && ttime.tm_hour <= 16) {

        one->pfs = one->pfs_v[ttime.tm_hour - start_hour];
        one->now_hour = ttime.tm_hour;
      }
    }
    one->now_t = now;

    //y是由結果產生的0~1的值， 之後要擲骰子確定是否要留下結果
    if (l_time_cs < one->s_time_cs)
      y = 1;
    else
      y = 1 / exp((l_time_cs - one->s_time_cs) / t0);

    //x是0~1隨機數，若y > x則採用組合，反之則否
    double x = nd(one->gen);

    // 接受結果
    if (y > x) {
      one->shortest_vec = one->now_vec;
      one->s_time_cs = l_time_cs;
	  (*print_message)[id].message1 = "\rIter: " + to_string(i) + " Temp: " + to_string(t0) + " Shortest Path: [ ";
	  for (auto j : one->now_vec)
      {
		(*print_message)[id].message1 += to_string(j) + " ";
	  }
	  (*print_message)[id].message1 += "] ";
	  (*print_message)[id].message1 += "Shortest Time: " + to_string(one->s_time_cs);

      /*cout << "\r\033[38;2;235;118;65m" << utf8.to_bytes(L"迭代次數: ") << i << " Temp: ";
      printf("%.3f                                                                       \033[0m\n", t0);
      cout << "Now: ";
      for (auto x : one->now_vec)
        cout << x << " ";
      cout << "  " << "Shortest: ";
      for (auto w : shortest_vec)
        cout << w << " ";
      cout << " Time cost: " << s_time_cs << endl;
      cout << "==============================================================================================================" << endl;*/


      //降溫
      t0 = t0 * 0.9;

      //嘗試次數變回0
      try_cnt = 0;

    }

    // 不接受結果
    else {
      i--;
      one->now_vec = one->shortest_vec;
      try_cnt++;
      (*print_message)[id].message2 = "Trying... Please wait... " + to_string(try_cnt) + '/' + to_string(int(TRY_MAX));

    }
    //遊歷路徑重新組合
    shuffle(one->now_vec.begin() + 1, one->now_vec.end() - 1, one->gen);
    /*int first = one->id_rand(one->gen);
    int second = one->id_rand(one->gen);
    while (first == second) {
      second = one->id_rand(one->gen);
    }
    swap(one->now_vec[first], one->now_vec[second]);*/
  }
  shared_counter--;
}



int main()
{
  g_map gm;
  time_t now;
  //int stay_time = 0;
  cout << utf8.to_bytes(L"歡迎使用郵局最短路徑計算程式") << endl << utf8.to_bytes(L"輸入起始時間 (ex. 12:03:04 或 -1 即現在時間 ps.資料由 AM 9:00 to PM 5:00): ");
  string s = "10:00:00";
  //cin >> s;
  //tm ttime;

  vector<unordered_map<int, post_office>> pfs_v;
  unordered_map<int, post_office> pfs;
  vector<int> pf_vec; //郵局順序
  vector<int> now_vec;

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

  nowtime = now;


  localtime_s(&ttime, &now);
  start_hour = ttime.tm_hour;
  now_hour = ttime.tm_hour;

  //vector<unordered_map<int, post_office>> pfs_v;

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
  /*random_device rd;
  int seed = rd();*/


  for (int i = 0; i < thread_num; i++)
  {
	seed[i] = rd();
	//s
	cout << "Seed" << i << ": " << seed[i] << endl;
  }

  //mt19937 gen(seed);
  //uniform_real_distribution <double> nd(0.0, 1.0); //隨機數變為均勻分佈(0~1)
  //uniform_int_distribution<> id(1, pfs.size() - 1);
  //uniform_int_distribution<> st(1, 20);

  //vector<int> pf_vec; //郵局順序
  //vector<int> shortest_vec; //郵局最短順序
  //int s_time_cs = 1e9; //移動的最短距離
  //int start = 0; //起始與終點郵局



  cout << utf8.to_bytes(L"開始時間: ");
  printf("%02d:%02d:%02d\n", ttime.tm_hour, ttime.tm_min, ttime.tm_sec);

  for (int i = 0; i < pfs.size(); i++) {

    if (i != 0 && i % 6 == 0)
      cout << endl << endl;

    cout << "[" << pfs[i].num << "] " << pfs[i].name << " ";
  }
  cout << endl << endl << utf8.to_bytes(L"輸入起點郵局(代碼): ");
  //cin >> start;
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

  now_vec = pf_vec;

  uniform_int_distribution<> id(1, pfs.size() - 1);
  //uniform_int_distribution<> it(1, pfs.size() - 1);

  vector <ddata*> one;
  //time_t nowtime[2] = {now_t};

  for (int j = 0; j < thread_num; j++)
  {
	one.push_back(new ddata());
  }
  
  for (int i = 0; i < thread_num; i++)
  {
    one[i]->now_hour = now_hour;
    one[i]->s_time_cs = s_time_cs;
    one[i]->pfs_v = pfs_v;
    one[i]->pfs = pfs;
    one[i]->now_t = nowtime;
    one[i]->now_vec = now_vec;
    one[i]->id_rand = id;
	one[i]->shortest_vec = now_vec;
    one[i]->gen = mt19937(seed[i]);

  }

  /*one[1]->now_hour = now_hour;
  one[1]->s_time_cs = s_time_cs;
  one[1]->pfs_v = pfs_v;
  one[1]->pfs = pfs;
  one[1]->now_t = nowtime;
  one[1]->now_vec = now_vec;
  one[1]->id_rand = id;
  one[1]->gen = mt19937(seed2);*/
  printf("\033[?25l");
  vector<thread> threads;

  thread t1(Printout);

  for (int i = 0; i < thread_num; i++) {
    threads.emplace_back(SA_test, ref(one[i]), i);
  //threads.emplace_back(SA_test, ref(one[1]),1);
  }

 
  for (auto& t : threads) {
    t.join();
  }

  t1.join();


  if (shared_counter == 0)
  {
    finish = true;
  }

  printf("\n\n\n");

  cout << endl;
  cout << "Shortest Time: " << one[0]->s_time_cs << endl;
  cout << "Path:" << endl;
  for (auto it = one[0]->shortest_vec.begin(); it != one[0]->shortest_vec.end(); it++) {

    if (it == one[0]->shortest_vec.begin())
      cout << one[0]->pfs[*it].name;
    else
      cout << " -> " << one[0]->pfs[*it].name;
  }
  cout << endl << endl;

  return 0;
}



