package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io"
	"os"
	"sort"
	"strings"
)

func main() {
	Test()
}

func Test() {
	var path = "/opt/elasticsearch-5.2.2/config/analysis/synonym_es.txt"
	var f, _ = os.Open(path)

	defer func() { var _ = f.Close() }()

	var reader = bufio.NewReader(f)

	var end_line = 0
	var line bytes.Buffer

	var arr [][]string

	var total_words = 0

	for {
		var b, is_prefix, err = reader.ReadLine()
		if err == io.EOF || end_line == 1000 {
			break
		}

		if is_prefix {
			line.Write(b)
			continue
		} else {
			line.Write(b)
			//end_line++
		}

		var words = strings.Split(line.String(), ",")

		var new_words = make(map[string]int)

		for _, word := range words {
			if word != "" {
				new_words[word] = 0
			}
		}

		/*同义词至少要有两个*/
		if len(new_words) > 1 {
			total_words += len(new_words)
			var _words = []string{}
			for word, _ := range new_words {
				_words = append(_words, word)
			}

			arr = append(arr, _words)
		} else {
			//fmt.Println(new_words)
		}

		line.Reset()
	}

	//fmt.Println("单词总数：", total_words)

	var m = make(map[string]int)
	var m1 = make(map[int]map[string]string)

	for i, item := range arr {
		//fmt.Println("****", i)
		var index = i + 1

		var m_inx = make(map[int]string)
		for _, word := range item {
			var i_value /*int*/, found = m[word]
			if found {
				m_inx[i_value] = ""
			}
		}

		if len(m_inx) > 1 /*找到不同的倒排索引，处理m1反序集合*/ {
			for i, _ := range m_inx {
				var set_m, found = m1[i]
				if !found {
					fmt.Println("error: not found")
					return
				}

				for word, _ := range set_m {
					m[word] = index

					var _, found = m1[index]
					if !found {
						m1[index] = make(map[string]string)
					}
					m1[index][word] = ""
				}

				delete(m1, i)
			}
		} else {
			for i, _ := range m_inx {
				index = i
			}
		}

		for _, word := range item {
			m[word] = index

			var _, found = m1[index]
			if !found {
				m1[index] = make(map[string]string)
			}
			m1[index][word] = ""
		}
	}

	var lst MapLst
	for _, item := range m1 {
		var m = Map{
			Len: len(item),
			M:   item,
		}

		lst = append(lst, &m)
	}

	sort.Sort(lst)
	for _, item := range lst {
		fmt.Println(item)
	}
}

type Map struct {
	Len int
	M   map[string]string
}

func (m *Map) String() string {
	var b bytes.Buffer
	var i = 0
	for word, _ := range m.M {
		var _, _ = b.WriteString(fmt.Sprintf("%s", word))
		if i < m.Len-1 {
			b.WriteString(",")
		}
		i += 1
	}

	return fmt.Sprintf("len:%-10d     %s", m.Len, b.String())
}

type MapLst []*Map

func (lst MapLst) Len() int {
	return len(lst)
}

func (lst MapLst) Less(i int, j int) bool {
	return lst[i].Len > lst[j].Len
}

func (lst MapLst) Swap(i int, j int) {
	var temp *Map = lst[i]
	lst[i] = lst[j]
	lst[j] = temp
}
