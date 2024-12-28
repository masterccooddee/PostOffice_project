package main

import (
	"fmt"
	"io"
	"os"
	"slices"
	"strconv"

	"github.com/tidwall/sjson"
)

func normalize() {
	var time []int

	for w := 9; w <= 16; w++ {
		jj, err := Open_file("data\\post_office_with_info_" + strconv.Itoa(w) + ".json")
		if err != nil {
			fmt.Println(err)
			return
		}
		for i := 0; i < 14; i++ {
			for j := 0; j < 14; j++ {
				if i == j {
					continue
				}
				t := jj.Get("post_office").GetIndex(i).Get("info").Get(strconv.Itoa(j)).GetIndex(1).MustInt()
				time = append(time, t)
			}

		}
	}
	t_min := slices.Min(time)

	for w := 9; w <= 16; w++ {
		file, err := os.Open("data\\post_office_with_info_" + strconv.Itoa(w) + "_normalize.json")
		if err != nil {
			fmt.Println(err)
		}

		data, err := io.ReadAll(file)
		if err != nil {
			fmt.Println(err)
		}
		file.Close()

		jj, _ := Open_file("data\\post_office_with_info_" + strconv.Itoa(w) + ".json")
		for i := 0; i < 14; i++ {
			for j := 0; j < 14; j++ {
				if i == j {
					continue
				}
				t := jj.Get("post_office").GetIndex(i).Get("info").Get(strconv.Itoa(j)).GetIndex(1).MustInt()
				s, _ := sjson.Set(string(data), "post_office."+strconv.Itoa(i)+".info.:"+strconv.Itoa(j)+".1", t-t_min)
				data = []byte(s)

			}

		}
		//fmt.Println(string(data))
		err = os.WriteFile("data\\post_office_with_info_"+strconv.Itoa(w)+"_normalize.json", data, 0666)
		if err != nil {
			fmt.Println(err)
		}

	}
}
