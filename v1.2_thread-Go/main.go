package main

import (
	"fmt"
	sa "pft/SA"
	"sync"
	"time"
)

var done chan bool
var wg sync.WaitGroup
var mg []sa.Out_msg

func print(mg *[]sa.Out_msg) {
	for {
		select {
		case <-done:
			return
		default:

			fmt.Print("ID: 0\n")
			fmt.Printf("%s                                   \n", (*mg)[0].Message1)
			fmt.Printf("%s                                    \n", (*mg)[0].Message2)
			fmt.Print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-\n")
			fmt.Print("ID: 1\n")
			fmt.Printf("%s                                      \n", (*mg)[1].Message1)

			fmt.Printf("%s                                     \n", (*mg)[1].Message2)
			fmt.Print("\033[7A")

		}
	}
}

func main() {

	done = make(chan bool)

	//reader := bufio.NewReader(os.Stdin)
	fmt.Print("輸入時間(12:00:00  -1為現在時間): ")
	// input_time, _ := reader.ReadString('\n')
	// input_time = strings.TrimSpace(input_time)
	input_time := "10:0:0"
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

	mg = make([]sa.Out_msg, 4)

	fmt.Print("\033[?25l")
	wg.Add(2)
	go print(&mg)
	go sa.SA(input_time, len(array), start, &wg, &mg, 0)
	go sa.SA(input_time, len(array), start, &wg, &mg, 1)

	wg.Wait()

	time.Sleep(1 * time.Millisecond)
	done <- true
	fmt.Print("\033[8B\033[0m")

}
