package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

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
	SQA(input_time, start)
}
