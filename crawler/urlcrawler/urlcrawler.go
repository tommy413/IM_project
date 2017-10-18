package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/PuerkitoBio/goquery"
	_ "github.com/lib/pq"
)

// config options
type Conf struct {
	RateLimit int
	BatchSize int
	LogFile   string
	Db        string
}

// target data
type aCase struct {
	CaseUrl string
	HistUrl string
}

// handle errors
func errHandler(err error, msg string) {
	if err != nil {
		log.Println(msg)
		log.Print(err)
	}
}

// construct search url from court/date
func urlFromDate(court string, date time.Time, page int) string {
	url := "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx?courtFullName=" + court
	url += "&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate=" + date.Format("20060102")
	url += "&edate=" + date.Format("20060102")
	url += "&page=" + strconv.Itoa(page)
	return url + "&id=&searchkw=&v_booktype=&deepsearch=&jmain="
}

// send search request and preparse with goquery
func searchRequest(court string, date time.Time, page int, client *http.Client) *goquery.Document {
	url := urlFromDate(court, date, page)
	req, err := http.NewRequest("GET", url, nil)
	errHandler(err, "Error creating search request")
	req.Header.Add("Referer", "http://jirs.judicial.gov.tw/FJUD/indexContent_1.aspx")

	res, err := client.Do(req)
	delay := 4
	for err != nil {
		log.Printf("Error executing search request, retrying in %d seconds\n", delay)
		log.Print(err)
		time.Sleep(time.Duration(delay) * time.Millisecond)
		if delay < 600 {
			delay = delay * 2
		}
		res, err = client.Do(req)
	}

	doc, err := goquery.NewDocumentFromResponse(res)
	errHandler(err, "Error parsing search response")

	return doc
}

// from preparsed page, find all case / history urls
func parseSearch(doc *goquery.Document) []aCase {
	var cases []aCase
	entries := doc.Find("#Table3").Find("TR")
	entries.Each(func(i int, s *goquery.Selection) {
		if i != 0 {
			links := s.Find("a")
			CaseUrl, _ := links.First().Attr("href")
			HistUrl, _ := links.Eq(1).Attr("href")
			thisCase := aCase{CaseUrl, HistUrl}
			if CaseUrl != "" || CaseUrl != "#" {
				cases = append(cases, thisCase)
			}
		}
	})
	return cases
}

func worker(db *sql.DB, client *http.Client, conf Conf) bool {
	// set prepared statements
	// getWork.Query(conf.BatchSize)
	getWork, err := db.Prepare("UPDATE raw_todo SET inProgress = TRUE WHERE id IN (SELECT id FROM raw_todo WHERE inProgress = FALSE ORDER BY id LIMIT $1) RETURNING *")
	errHandler(err, "Error preparing get work statement")
	// saveWork.Exec(id, caseUrl, histUrl, inprogress=0)
	saveWork, err := db.Prepare("INSERT INTO raw_urls VALUES ($1, $2, $3, $4)")
	errHandler(err, "Error preparing save work statement")
	// updateWork.Exec(id_from_getWork)
	updateWork, err := db.Prepare("DELETE FROM raw_todo WHERE id = $1")
	errHandler(err, "Error preparing update work statement")

	rows, err := getWork.Query(conf.BatchSize)
	errHandler(err, "Error querying db for work")
	notEmpty := false
	for rows.Next() {
		notEmpty = true
		var jobid int
		var court, sd, ed string
		var mod bool
		err = rows.Scan(&jobid, &court, &sd, &ed, &mod)
		errHandler(err, "Error scanning rows")
		log.Printf("Job received: %d %s %s %s\n", jobid, court, sd, ed)

		sdate, err := time.Parse("2006-01-02", sd)
		errHandler(err, "Error parsing start date")
		edate, err := time.Parse("2006-01-02", ed)
		errHandler(err, "Error parsing end date")

		for d := sdate; d.Before(edate.AddDate(0, 0, 1)); d = d.AddDate(0, 0, 1) {
			if d != sdate {
				time.Sleep(time.Duration(conf.RateLimit) * time.Millisecond)
			}
			baseid := court + d.Format("20060102")
			log.Println("Working on: " + baseid)

			// first page
			doc := searchRequest(court, d, 1, client)
			cases := parseSearch(doc)

			// other pages
			pages := doc.Find("select").First().Find("option").Length()
			for p := 2; p <= pages; p++ {
				time.Sleep(time.Duration(conf.RateLimit) * time.Millisecond)
				doc := searchRequest(court, d, p, client)
				cases = append(cases, parseSearch(doc)...)
			}

			// save results to database
			for index, c := range cases {
				id := baseid + fmt.Sprintf("%60d", index)
				_, err = saveWork.Exec(id, c.CaseUrl, c.HistUrl, false)
				errHandler(err, "Error saving url to db: "+id)
			}
			log.Println("Completed: " + baseid)
		}

		_, err = updateWork.Exec(jobid)
		errHandler(err, "Error updating raw_todo")
		log.Printf("Job completed: %d\n", jobid)
	}
	return notEmpty
}

func main() {
	// parse config
	var conf Conf
	_, err := toml.DecodeFile("config.toml", &conf)
	errHandler(err, "Error decoding config")

	// set logging
	if conf.LogFile != "" {
		l, err := os.OpenFile(conf.LogFile, os.O_RDWR|os.O_APPEND, 0660)
		errHandler(err, "Error creating log file: "+conf.LogFile)
		log.SetOutput(l)
		log.Println("Logging started")
	}

	// set DB
	db, err := sql.Open("postgres", "postgres://"+conf.Db)
	errHandler(err, "Error opening db connection")
	err = db.Ping()
	errHandler(err, "Error pinging db")
	if err != nil {
		return
	}
	log.Println("Connected to DB")

	// setup client for reuse
	client := &http.Client{}

	//
	next := worker(db, client, conf)
	for next != false {
		next = worker(db, client, conf)
	}
}
