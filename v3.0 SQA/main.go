package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strings"
	"sync"
	"time"
)

var (
	total_iter int = 1e6
	wg         sync.WaitGroup
	msg        MMSg
	Threads    int = 20
	done           = make(chan struct{})
)

func print(mg *MMSg) {
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
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("輸入時間(12:00:00  -1為現在時間): ")
	input_time, _ := reader.ReadString('\n')
	input_time = strings.TrimSpace(input_time)

	jj, err := Open_file("data\\post_office_with_info_9.json")
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
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

	iter_per_thread := total_iter / Threads
	msg = make(MMSg, Threads)

	fmt.Print("\033[?25l")
	wg.Add(Threads)

	go print(&msg)

	eval_start := time.Now()
	for i := 0; i < Threads; i++ {
		alpha_coff := float32(i) / float32(Threads-1)
		go SQA(input_time, start, iter_per_thread, &wg, &msg, i, alpha_coff)
	}

	wg.Wait()
	eval_cost := int(time.Since(eval_start).Seconds())

	time.Sleep(1 * time.Millisecond)
	done <- struct{}{}
	fmt.Printf("\033[%dB\033[0m", Threads*3+Threads)
	fmt.Println()

	for i := range msg {
		if msg[i].S_r == nil {
			msg[i].Ttime = 1e9
		}
	}

	sort.Sort(msg)

	shortest_route := msg[0].S_r
	fmt.Printf("最短路徑: %v Time: \033[38;2;230;193;38m%d\033[0m 秒 🚛抵達時間： %s\n", msg[0].S_r, msg[0].Ttime, msg[0].Arrive_time)

	for index, pf := range shortest_route {
		if index != len(shortest_route)-1 {
			fmt.Printf("%s ⇨ ", jj.Get("post_office").GetIndex(pf).Get("name").MustString())
		} else {
			fmt.Printf("%s\n", jj.Get("post_office").GetIndex(pf).Get("name").MustString())
		}

	}
	benchmark := msg[0].Ttime * eval_cost
	fmt.Printf("Benchmark = %d x  %d = %d \n", msg[0].Ttime, eval_cost, benchmark)

	fmt.Print("\033[?25h")
	fmt.Scanln()
}
