package main

import (
	"bufio"
	"fmt"
	"os"
	sa "pft/SA"
	"sort"
	"strings"
	"sync"
	"time"
)

var done chan bool
var wg sync.WaitGroup
var mg []sa.Out_msg

const Threads = 8

func print(mg *[]sa.Out_msg) {
	lineCounter := 0
	p_time := 0
	for {
		select {
		case <-done:
			return
		default:

			for i := 0; i < Threads; i++ {

				if lineCounter >= 5 && p_time == 0 {
					fmt.Printf("\033[s\033[%dB\033[u", 20)
					lineCounter = 0
					p_time++
				}

				fmt.Printf("ID: %d\n", i)
				fmt.Printf("%s                                   \n", (*mg)[i].Message1)
				fmt.Printf("%s                                    \n", (*mg)[i].Message2)
				if i != Threads-1 {
					fmt.Print("\033[38;2;235;118;65m+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\033[0m\n")

				}
				lineCounter += 4

			}
			up := Threads*3 + Threads - 1
			fmt.Printf("\033[%dA", up)

		}
	}
}

func main() {

	done = make(chan bool)

	reader := bufio.NewReader(os.Stdin)
	fmt.Print("輸入時間(12:00:00  -1為現在時間): ")
	input_time, _ := reader.ReadString('\n')
	input_time = strings.TrimSpace(input_time)

	fmt.Println()
	jj, err := sa.Open_file("data\\post_office_with_info_9.json")
	if err != nil {
		fmt.Println(err)
		return
	}

	array, _ := jj.Get("post_office").Array()

	// 郵局選擇
	for i := 0; i < len(array); i++ {
		if i == 9 {
			fmt.Printf("[%2d] %-10s", i, jj.Get("post_office").GetIndex(i).Get("name").MustString())
			continue
		} else if i >= 10 && i != 11 {
			fmt.Printf("[%2d] %-12s", i, jj.Get("post_office").GetIndex(i).Get("name").MustString())

		} else {
			fmt.Printf("[%2d] %-11s", i, jj.Get("post_office").GetIndex(i).Get("name").MustString())
		}

		if i%6 == 0 && i != 0 {
			fmt.Println()
		}

	}
	fmt.Println()

	var start int
	fmt.Print("輸入起始郵局: ")
	fmt.Scanf("%d\n", &start)
	fmt.Println()

	mg = make([]sa.Out_msg, Threads)

	fmt.Print("\033[?25l")
	wg.Add(Threads)

	go print(&mg)

	for i := 0; i < Threads; i++ {

		go sa.SA(input_time, len(array), start, &wg, &mg, i)
	}

	wg.Wait() //等待所有SA goroutine完成

	time.Sleep(1 * time.Millisecond)
	done <- true //結束print goroutine
	fmt.Printf("\033[%dB\033[0m", Threads*3+Threads)
	fmt.Println()

	sort.Sort(sa.MMSg(mg))

	shortest_route := mg[0].S_r
	fmt.Printf("最短路徑: %v Time: \033[38;2;230;193;38m%d\033[0m 秒 🚛抵達時間： %s\n", mg[0].S_r, mg[0].Ttime, mg[0].Arrive_time)

	for index, pf := range shortest_route {
		if index != len(shortest_route)-1 {
			fmt.Printf("%s ⇨ ", jj.Get("post_office").GetIndex(pf).Get("name").MustString())
		} else {
			fmt.Printf("%s\n", jj.Get("post_office").GetIndex(pf).Get("name").MustString())
		}

	}

	time.Sleep(5 * time.Minute)

}
