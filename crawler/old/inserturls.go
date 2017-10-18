package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"log"
	"os"
	"strconv"
	"time"

	_ "github.com/lib/pq"
)

// Individual case / page url
// Also includes link to page referencing historical cases
// urls are relative
type aCase struct {
	CaseUrl string
	HistUrl string
}

// All the cases of a court/type on a particular day
type caseList struct {
	Court string
	Date  time.Time
	Cases []aCase
}

func errHandler(err error, msg string) {
	if err != nil {
		log.Println(msg)
		log.Print(err)
	}
}

func padI2S(num int, l int) string {
	out := strconv.Itoa(num)
	for len(out) < l {
		out = "0" + out
	}
	return out
}

func main() {

	var db *sql.DB
	db, err := sql.Open("postgres", "postgres://datac1:datac15543@127.0.0.1/law1")
	errHandler(err, "Error opening db connection")

	err = db.Ping()
	errHandler(err, "Error pinging db")

	stmt, err := db.Prepare("INSERT INTO raw_urls VALUES ($1, $2, $3)")
	errHandler(err, "Error preparing db statement")

	f2, err := os.OpenFile("nextTimeUrls.json", os.O_RDWR|os.O_APPEND, 0660)
	errHandler(err, "Open file")
	defer f2.Close()

	f, err := os.Open("allUrls.json")
	errHandler(err, "Open file")
	defer f.Close()
	s := bufio.NewScanner(f)

	const maxCapacity = 1024 * 1024
	buf := make([]byte, maxCapacity)
	s.Buffer(buf, maxCapacity)

	for s.Scan() {
		var data caseList
		err = json.Unmarshal(s.Bytes(), &data)
		errHandler(err, "Unmarshal")

		baseid := data.Court + data.Date.Format("20060102")

		for index, acase := range data.Cases {
			id := baseid + padI2S(index, 3)
			if acase.CaseUrl == "" {
				continue
			}
			_, err = stmt.Exec(id, acase.CaseUrl, acase.HistUrl)
			errHandler(err, "Error inserting data into db: "+id)
			log.Println("Done: " + id)
		}
	}
	log.Println("ALL DONE?")
}
