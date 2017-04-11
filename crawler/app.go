package main

import (
	"bufio"
	"database/sql"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
	_ "github.com/lib/pq"
)

// Message from main() to searchWorker
// court is courtName + type
type searchParams struct {
	court     string
	startDate time.Time
	endDate   time.Time
}

// Individual case / page url
// Also includes link to page referencing historical cases
// urls are relative
type aCase struct {
	caseUrl string
	histUrl string
}

// All the cases of a court/type on a particular day
type caseList struct {
	court string
	date  time.Time
	cases []aCase
}

// Tells crawlers where to put the resulting htmls
// only one of location or db should be used
type outMode struct {
	mode     string
	location string
	db       *sql.DB
}

func errHandler(err error, msg string) {
	if err != nil {
		log.Println(msg)
		log.Print(err)
	}
}

// construct search url from court/date
func urlFromDate(court string, date time.Time, page int) string {
	url := "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx?courtFullName="
	url += court
	url += "&v_sys=M&jud_year=&jud_case=&jud_no=&jud_no_end=&jud_title=&keyword=&sdate="
	url += date.Format("20060102")
	url += "&edate="
	url += date.Format("20060102")
	url += "&page="
	url += strconv.Itoa(page)
	url += "&id=&searchkw=&v_booktype=&deepsearch=&jmain="
	return url
}

// send search request and preparse with goquery
func searchRequest(court string, date time.Time, page int, client *http.Client) *goquery.Document {
	url := urlFromDate(court, date, page)
	req, err := http.NewRequest("GET", url, nil)
	errHandler(err, "Error creating search request")
	req.Header.Add("Referer", "http://jirs.judicial.gov.tw/FJUD/indexContent_1.aspx")

	res, err := client.Do(req)
	errHandler(err, "Error executing search request")

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
			caseUrl, _ := links.First().Attr("href")
			histUrl, _ := links.Eq(1).Attr("href")
			thisCase := aCase{caseUrl, histUrl}
			cases = append(cases, thisCase)
		}
	})
	return cases
}

func padI2S(num int, l int) string {
	out := strconv.Itoa(num)
	for len(out) < l {
		out = "0" + out
	}
	return out
}

// split date range into days
// search each result page for each day
// create list of urls to crawl
func searchWorker(client *http.Client, jobs <-chan searchParams, crawleChan chan caseList, exitChan chan int) {
	for j := range jobs {
		for d := j.startDate; d.Before(j.endDate.AddDate(0, 0, 1)); d = d.AddDate(0, 0, 1) {
			fmt.Println("Searcher: " + d.Format("2006-01-02"))
			doc := searchRequest(j.court, d, 1, client)
			cases := parseSearch(doc)

			pages := doc.Find("select").First().Find("option").Length()
			for p := 2; p <= pages; p++ {
				doc := searchRequest(j.court, d, p, client)
				cases = append(cases, parseSearch(doc)...)
			}

			caseList := caseList{j.court, d, cases}
			crawleChan <- caseList
			exitChan <- 1
		}
	}
}

func crawlPage(client *http.Client, url string, referer string) []byte {
	req, err := http.NewRequest("GET", url, nil)
	errHandler(err, "Error creating crawl request")
	req.Header.Add("Referer", referer)
	res, err := client.Do(req)
	errHandler(err, "Error executing crawl request")
	defer res.Body.Close()
	data, err := ioutil.ReadAll(res.Body)
	errHandler(err, "Error reading response")
	return data
}

// for each page download and save it
func crawlerWorker(client *http.Client, outMode outMode, jobs <-chan caseList, exitChan chan int) {
	baseUrl := "http://jirs.judicial.gov.tw/FJUD/"
	referer := "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx"

	for j := range jobs {
		fmt.Println("Crawler: " + j.date.Format("2006-01-02"))

		path := outMode.location + "/" + j.court + "/" + j.date.Format("2006-01-02") + "/"
		if outMode.mode == "fs" {
			os.MkdirAll(path, os.ModePerm)
		}

		for index, c := range j.cases {
			caseHtml := crawlPage(client, baseUrl+c.caseUrl, referer)
			histHtml := crawlPage(client, baseUrl+c.histUrl, referer)

			if outMode.mode == "fs" {
				ioutil.WriteFile(path+strconv.Itoa(index)+".html", caseHtml, os.ModePerm)
				ioutil.WriteFile(path+strconv.Itoa(index)+"-h.html", histHtml, os.ModePerm)
			} else {
				id := j.court + j.date.Format("20060102") + padI2S(index, 3)
				stmt, err := outMode.db.Prepare("INSERT INTO raw_data VALUES ($1, $2, $3, $4, $5, $6)")
				errHandler(err, "Error preparing db statement")
				_, err = stmt.Exec(id, j.court[:3], j.court[3:4], j.date.Format("2006-01-02"), string(caseHtml), string(histHtml))
				errHandler(err, "Error inserting data into db")
			}
		}

		fmt.Println("Crawler: " + j.date.Format("2006-01-02") + " Complete")
		exitChan <- -1
	}
}

// CREATE TABLE `raw_data` (
//   `id` VARCHAR(15) NOT NULL DEFAULT 'NULL',
//   `court` VARCHAR(5) NOT NULL DEFAULT 'NULL',
//   `type` CHAR(1) NOT NULL DEFAULT 'NULL',
//   `date` DATE NOT NULL DEFAULT 'NULL',
//   `caseHtml` MEDIUMTEXT NULL DEFAULT NULL,
//   `historyHtml` MEDIUMTEXT NULL DEFAULT NULL,
//   PRIMARY KEY (`id`)
// );

func connectDb(login string) *sql.DB {
	db, err := sql.Open("postgres", "postgres://"+login)
	errHandler(err, "Error opening db connection")

	err = db.Ping()
	errHandler(err, "Error pinging db")

	return db
}

func input2Chan(args []string, searchChan chan searchParams) {
	sdate, err := time.Parse("20060102", args[1])
	errHandler(err, "Error parsing start date")
	edate, err := time.Parse("20060102", args[2])
	errHandler(err, "Error parsing end date")

	searchChan <- searchParams{args[0], sdate, edate}

}

func main() {
	// parse flags for modes
	inputfile := flag.String("f", "none", "file of input args")
	outputfs := flag.String("fs", "downloaded", "location of output dirs")
	outputdb := flag.String("db", "none", "user:pass@host:port/db")

	flag.Parse()

	if (*outputfs)[len(*outputfs)-1:] == "/" {
		*outputfs = (*outputfs)[:len(*outputfs)-1]
	}

	outMode := outMode{"fs", *outputfs, nil}
	if *outputdb != "none" {
		outMode.mode = "db"
		outMode.db = connectDb(*outputdb)
	}

	// create channels
	client := &http.Client{}

	searchChan := make(chan searchParams, 10)
	crawleChan := make(chan caseList, 100)
	exitChan := make(chan int, 10)

	// start workers
	go searchWorker(client, searchChan, crawleChan, exitChan)
	for i := 0; i < 2; i++ {
		go crawlerWorker(client, outMode, crawleChan, exitChan)
	}

	// parse for work
	if *inputfile == "none" {
		input2Chan(flag.Args(), searchChan)
	} else {
		file, err := os.Open(os.Args[2])
		errHandler(err, "Error opening file list")
		defer file.Close()
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			input2Chan(strings.Split(scanner.Text(), " "), searchChan)
		}
	}

	// wait for exit
	counter := 0 + <-exitChan
	for counter > 0 {
		counter += <-exitChan
	}
}
