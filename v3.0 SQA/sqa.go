package main

import (
	"fmt"
	"io"
	"math"
	"math/rand"
	"os"
	"strconv"

	"github.com/bitly/go-simplejson"
)

var (
	iter_time               = 1000
	temp            float64 = 1e3
	transverseField float64 = 1e4
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

func show_matrix(matrix [][]int) {
	for i := 0; i < len(matrix); i++ {
		fmt.Println(matrix[i])
	}
}

func main() {

	jj, err := Open_file("data\\post_office_with_info_10.json")
	if err != nil {
		fmt.Println(err)
		return
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
			//time_matrix[i][j] = 10000
		}

	}
	fmt.Println("time_matrix")
	show_matrix(time_matrix)

	// make spin matrix
	spin_matrix := make([][]int, N)
	for i := 0; i < N; i++ {
		spin_matrix[i] = make([]int, N)
	}

	for i := 0; i < N; i++ {
		for j := 0; j < N; j++ {
			spin_matrix[i][j] = rand.Intn(2)*2 - 1
		}
	}
	fmt.Println("spin_matrix")
	show_matrix(spin_matrix)

	// make local field matrix
	localField_matrix := make([][]int, N)
	for i := 0; i < N; i++ {
		localField_matrix[i] = make([]int, N)
	}

	for m := 0; m < N; m++ {
		for i := 0; i < N; i++ {
			for j := 0; j < N; j++ {
				localField_matrix[i][m] += time_matrix[i][j] * spin_matrix[j][m]
			}
		}
	}
	fmt.Println("localField_matrix")
	show_matrix(localField_matrix)
	var deltaH float64
	var transverseField2 float64
	jdagger := temp / 2 * math.Log(math.Cosh(float64(transverseField)/(float64(N)*temp))/math.Sinh(float64(transverseField)/(float64(N)*temp)))

	for t := 0; t < iter_time; t++ {
		for i := 0; i < N; i++ {
			for m := 0; m < N; m++ {
				if m == 0 {
					deltaH = float64(spin_matrix[i][m]) * (float64(localField_matrix[i][m]) - jdagger*float64((spin_matrix[i][m+1])))
				} else if m == N-1 {
					deltaH = float64(spin_matrix[i][m]) * (float64(localField_matrix[i][m]) - jdagger*float64((spin_matrix[i][m-1])))
				} else {
					deltaH = float64(spin_matrix[i][m]) * (float64(localField_matrix[i][m]) - jdagger*float64((spin_matrix[i][m+1]+spin_matrix[i][m-1])))
				}
				fmt.Println("deltaH", deltaH)

				if math.Exp(-deltaH/temp) > rand.Float64() {
					spin_matrix[i][m] = -spin_matrix[i][m]

					for j := 0; j < N; j++ {
						localField_matrix[j][m] += 2 * time_matrix[i][j] * spin_matrix[i][m]
					}

					fmt.Println("temp", temp)
				}

			}
		}
		temp *= 0.9
		transverseField2 = transverseField * (1 - float64(t+1)/float64(iter_time))
		jdagger = temp / 2 * math.Log(math.Cosh(float64(transverseField2)/(float64(N)*temp))/math.Sinh(float64(transverseField2)/(float64(N)*temp)))
		fmt.Println(t)
		fmt.Println("transverseField", transverseField2)
		fmt.Println("temp", temp)
		fmt.Println("jdagger", jdagger)
		show_matrix(spin_matrix)
	}

}
