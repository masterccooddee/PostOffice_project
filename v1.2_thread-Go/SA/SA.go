package sa

import (
	"fmt"
	"io"
	"math"
	"math/rand"
	"os"
	"strconv"
	"sync"
	"time"

	"github.com/bitly/go-simplejson"
)

type Out_msg struct {
	Message1 string
	Message2 string
	count    int
}

func Open_file(f string) (*simplejson.Json, error) {
	file, err := os.Open(f)
	if err != nil {
		return nil, err
	} else {
		//fmt.Println("File opened successfully")
	}

	defer file.Close()

	data, err := io.ReadAll(file)
	if err != nil {
		fmt.Println(err)
		return nil, err
	}

	j, _ := simplejson.NewJson(data)

	return j, nil

}

func time_cost(route []int, j []*simplejson.Json, n_t time.Time) (int, time.Time) {
	var time_cost int
	var dur int
	var index int

	now_time := n_t
	for i := 0; i < len(route)-1; i++ {

		if n_t.Hour() <= 16 {

			index = n_t.Hour() - now_time.Hour()

		} else {
			index = len(j) - 1
		}
		dur = j[index].Get("post_office").GetIndex(route[i]).Get("info").Get(strconv.Itoa(route[i+1])).GetIndex(1).MustInt()
		time_cost += dur
		n_t = n_t.Add(time.Duration(dur) * time.Second)
		//fmt.Println(dur, n_t)
	}

	return time_cost, n_t
}

func SA(input_time string, size int, start int, wg *sync.WaitGroup, output_s *[]Out_msg, id int) {

	defer wg.Done()

	const T0 int = 1e6         //initial temperature
	const iter int = 250       //iteration times
	const alpha float64 = 0.9  //cooling rate
	const T_end float64 = 1e-1 //end temperature
	const TRY_MAX int = 0.9e8  //max try times

	//enter time
	var hour, min, second int
	var now_time time.Time

	if input_time == "-1" {
		now_time = time.Now()
		hour = now_time.Hour()
		min = now_time.Minute()
		second = now_time.Second()
	} else {
		fmt.Sscanf(input_time, "%d:%d:%d", &hour, &min, &second)
		now_time = time.Date(2024, time.September, 24, hour, min, second, 0, time.Local)
	}

	var j_s []*simplejson.Json

	for i := 0; i < 4; i++ {

		n_h := hour + i
		var j *simplejson.Json
		if n_h > 16 {
			break
		}

		file_name := "data\\post_office_with_info_" + strconv.Itoa(n_h) + ".json"
		j, err := Open_file(file_name)
		if err != nil {
			fmt.Println(err)
			return
		}
		j_s = append(j_s, j)
	}

	//初始郵局路徑
	var pf_route []int
	pf_route = append(pf_route, start)
	for i := 0; i < size; i++ {
		if i == start {
			continue
		}
		pf_route = append(pf_route, i)
	}
	pf_route = append(pf_route, start)

	var l_time_cost int
	var s_time_cost int
	var y float64
	var shortest_route []int
	var temperature float64

	s_time_cost = 1e9
	temperature = float64(T0)
	now_route := pf_route
	var try_count int

	var timestamp_s time.Time
	//SA
	for i := 0; i < iter; i++ {

		if try_count >= TRY_MAX {
			(*output_s)[id].Message1 = fmt.Sprintf("\rTry over %d times", TRY_MAX)
			(*output_s)[id].count += 1
			break
		}
		if temperature <= T_end {
			(*output_s)[id].Message1 = fmt.Sprintf("\rTemperature is lower than %.3f", T_end)
			(*output_s)[id].count += 1
			break
		}

		now := now_time

		time_c, now := time_cost(now_route, j_s, now)
		l_time_cost = time_c
		if l_time_cost < s_time_cost {
			y = 1
		} else {
			y = 1 / math.Exp((float64(l_time_cost)-float64(s_time_cost))/float64(temperature))
		}

		x := rand.Float64()

		if y > x {
			shortest_route = now_route
			s_time_cost = l_time_cost
			//arrival_time := now.Format("PM 03:04:05")

			(*output_s)[id].Message1 = fmt.Sprintf("\r第%d次迭代 Temp: %.3f 最短路徑: %v Time: %d 秒", i+1, temperature, shortest_route, s_time_cost)
			(*output_s)[id].count += 1
			//fmt.Println("----------------------------------------------------------------------")

			//cool down
			temperature *= alpha
			try_count = 0

		} else {
			i--
			try_count++
			if try_count == 1 {
				timestamp_s = time.Now()
			}
			now_route = shortest_route

			// 計算經過的時間
			elapsed := time.Since(timestamp_s)
			totalSeconds := int(elapsed.Seconds())
			minutes := totalSeconds / 60
			seconds := totalSeconds % 60

			(*output_s)[id].Message2 = fmt.Sprintf("\rTrying please wait... %d/%d  %d%% [%02d : %02d]", try_count, TRY_MAX, (try_count*100)/TRY_MAX, minutes, seconds)
			//fmt.Println(now_route)
		}

		//random change swap
		// first := rand.Intn(13) + 1
		// second := rand.Intn(13) + 1
		// for first == second {
		// 	second = rand.Intn(13) + 1
		// }
		// now_route[first], now_route[second] = now_route[second], now_route[first]

		//random change shuffle
		rand.Shuffle(len(now_route)-2, func(i, j int) { now_route[i+1], now_route[j+1] = now_route[j+1], now_route[i+1] })
	}

	(*output_s)[id].Message1 = fmt.Sprintf("\rFinish Shortest Route: %v Time: %d", shortest_route, s_time_cost)
	// fmt.Print("最短路徑: ")
	// for index, pf := range shortest_route {
	// 	if index != len(shortest_route)-1 {
	// 		fmt.Printf("%s ⇨ ", j_s[0].Get("post_office").GetIndex(shortest_route[pf]).Get("name").MustString())
	// 	} else {
	// 		fmt.Printf("%s\n", j_s[0].Get("post_office").GetIndex(shortest_route[pf]).Get("name").MustString())
	// 	}

	// }

	//time.Sleep(5 * time.Minute)
}
