package main

import (
	"fmt"
	"io"
	"math"
	"math/rand"
	"os"
	"slices"
	"strconv"
	"time"

	"github.com/bitly/go-simplejson"
)

var (
	iter_time int = 5e7
	epson         = 1e-3
)

func Open_file(f string) (*simplejson.Json, error) {
	file, err := os.Open(f)
	if err != nil {
		return nil, err
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

func make_matrix(s string) [][]int {
	jj, err := Open_file(s)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	array, _ := jj.Get("post_office").Array()
	N := len(array)

	time_matrix := make([][]int, N)
	for i := 0; i < N; i++ {
		time_matrix[i] = make([]int, N)
	}
	// make coupling matrix
	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			if i == j {
				time_matrix[i][j] = 0
				continue
			}
			time_matrix[i][j] = jj.Get("post_office").GetIndex(i).Get("info").Get(strconv.Itoa(j)).GetIndex(1).MustInt()

		}

	}
	return time_matrix
}

func find_max(matrix [][][]int) int {
	var time []int

	for _, m := range matrix {
		for i := 0; i < len(m); i++ {
			time = append(time, m[i]...)
		}
	}
	return slices.Max(time)
}

func show_matrix(matrix [][]int) {
	for i := 0; i < len(matrix); i++ {
		fmt.Println(matrix[i])
	}
}

// time_cost (Energry)
func time_cost(route [][]int, dis_matrix [][][]int, n_t time.Time, alpha float32) (float32, time.Time) {
	var time_cost int
	var index int
	var h1 int
	var h2 int

	now_time_l := n_t
	index = n_t.Hour() - now_time_l.Hour()
	//time
	for i := 0; i < len(route); i++ {
		// first city
		for j := 0; j < len(route); j++ {
			// second city
			for k := 0; k < len(route); k++ {
				if i != len(route)-1 {
					time_cost += dis_matrix[index][j][k] * route[i][j] * route[i+1][k]
					n_t = n_t.Add(time.Duration(dis_matrix[index][j][k]*route[i][j]*route[i+1][k]) * time.Second)
				} else {
					time_cost += dis_matrix[index][j][k] * route[i][j] * route[0][k]
					n_t = n_t.Add(time.Duration(dis_matrix[index][j][k]*route[i][j]*route[0][k]) * time.Second)
				}

				//處理跨越時間
				if n_t.Hour() <= 16 {

					index = n_t.Hour() - now_time_l.Hour()

				} else {
					index = len(dis_matrix) - 1
				}
			}
		}

	}

	tmp := 0
	//計算penalty
	for t := 0; t < len(route); t++ {
		for i := 0; i < len(route); i++ {
			tmp += route[t][i]
		}
		h1 += (tmp - 1) * (tmp - 1)
		tmp = 0
	}
	tmp = 0
	for i := 0; i < len(route); i++ {
		for t := 0; t < len(route); t++ {
			tmp += route[t][i]
		}
		h2 += (tmp - 1) * (tmp - 1)
		tmp = 0
	}

	total_cost := float32(time_cost) + float32(h1)*alpha + float32(h2)*alpha
	// fmt.Print("\r")
	// fmt.Print("h1:", h1, "h2:", h2, "alpha:", alpha, "time cost:", time_cost)
	fmt.Printf("\rtime cost: %5d, alpha: %2f, h1: %d, h2: %d", time_cost, alpha, h1, h2)
	return total_cost, n_t
}

func SQA(input_time string, start int) {

	//enter time
	var hour, min, second int
	var now_time time.Time
	var t_matrix_slice [][][]int

	if input_time == "-1" {
		now_time = time.Now()
		hour = now_time.Hour()
		min = now_time.Minute()
		second = now_time.Second()
	} else {
		fmt.Sscanf(input_time, "%d:%d:%d", &hour, &min, &second)
		now_time = time.Date(2024, time.December, 25, hour, min, second, 0, time.Local)
	}

	for i := 0; i < 4; i++ {

		n_h := hour + i
		if n_h > 16 {
			break
		}
		file_name := "data\\post_office_with_info_" + strconv.Itoa(n_h) + ".json"
		t_matrix_slice = append(t_matrix_slice, make_matrix(file_name))
	}

	t_max := find_max(t_matrix_slice)

	// city_time_matrix
	var ct_matrix = make([][]int, len(t_matrix_slice[0]))
	for i := 0; i < len(t_matrix_slice[0]); i++ {
		ct_matrix[i] = make([]int, len(t_matrix_slice[0]))
		if i == 0 {
			continue
		}
		random_walk := rand.Intn(len(t_matrix_slice[0]))
		ct_matrix[i][random_walk] = 1
	}
	ct_matrix[0][start] = 1

	best_time := float32(math.MaxFloat32)

	for i := 0; i < iter_time; i++ {
		alpha := (float32(i)/float32(5))*float32(t_max) + float32(epson)
		t_c, depart := time_cost(ct_matrix, t_matrix_slice, now_time, alpha)
		if t_c < best_time {
			best_time = t_c
			fmt.Print("\n")
			show_matrix(ct_matrix)
			fmt.Println("\rbest time: ", best_time, "alpha: ", alpha, "iter: ", i, "depart time: ", depart)

		}
		// flip bit
		for j := 1; j < len(ct_matrix); j++ {

			random_walk := rand.Intn(len(t_matrix_slice[0]))
			ct_matrix[j] = make([]int, len(t_matrix_slice[0]))
			ct_matrix[j][random_walk] = 1

		}
	}

}
