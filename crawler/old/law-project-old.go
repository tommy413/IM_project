package main

import (
	"bufio"
	"database/sql"
	"encoding/json"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/BurntSushi/toml"
	"github.com/PuerkitoBio/goquery"
	_ "github.com/lib/pq"
)

type Config struct {
	General struct {
		MaxThreads int
		RateLimit  int
		LogFile    string
	}
	Searcher struct {
		InputFile  string
		OutputFile string
	}
	Crawler crawlerConf
}

type crawlerConf struct {
	InputFile string
	OutMode   string
	OutDir    string
	Login     string
}

type searchJobs struct {
	court string
	sdate time.Time
	edate time.Time
}

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
			CaseUrl, _ := links.First().Attr("href")
			HistUrl, _ := links.Eq(1).Attr("href")
			thisCase := aCase{CaseUrl, HistUrl}
			cases = append(cases, thisCase)
		}
	})
	return cases
}

// parses inputFile
func searchWorker(client *http.Client, inputFile string, outputFile string, rateLimit int) {
	// parse input file for court / date range
	file, err := os.Open(inputFile)
	errHandler(err, "Error opening input file list")
	defer file.Close()
	scanner := bufio.NewScanner(file)
	var jobs []searchJobs
	for scanner.Scan() {
		parts := strings.Split(scanner.Text(), " ")
		sdate, err := time.Parse("20060102", parts[1])
		errHandler(err, "Error parsing start date")
		edate, err := time.Parse("20060102", parts[2])
		errHandler(err, "Error parsing end date")
		jobs = append(jobs, searchJobs{parts[0], sdate, edate})
	}

	// todo is everything that needs to be crawled
	// also needs to be serialized into json
	f, err := os.OpenFile(outputFile, os.O_RDWR|os.O_APPEND, 0660)
	errHandler(err, "Error Opening outputFile")
	defer f.Close()
	for _, j := range jobs {
		for d := j.sdate; d.Before(j.edate.AddDate(0, 0, 1)); d = d.AddDate(0, 0, 1) {
			log.Println("Searcher: " + j.court + " " + d.Format("2006-01-02"))
			doc := searchRequest(j.court, d, 1, client)
			cases := parseSearch(doc)

			pages := doc.Find("select").First().Find("option").Length()
			for p := 2; p <= pages; p++ {
				doc := searchRequest(j.court, d, p, client)
				cases = append(cases, parseSearch(doc)...)
			}

			aCaseList := caseList{j.court, d, cases}
			data, err := json.Marshal(aCaseList)
			errHandler(err, "Error marshalling searcher result to json")
			f.Write(data)
			f.WriteString(",\n")

			time.Sleep(time.Duration(rateLimit) * time.Millisecond)
		}
	}
}

func padI2S(num int, l int) string {
	out := strconv.Itoa(num)
	for len(out) < l {
		out = "0" + out
	}
	return out
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
func crawlerWorker(client *http.Client, jobs <-chan caseList, conf crawlerConf, db *sql.DB, rateLimit int) {
	defer wg.Done()
	baseUrl := "http://jirs.judicial.gov.tw/FJUD/"
	referer := "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx"

	for j := range jobs {
		if j.Court == "exit" {
			break
		}

		log.Println("Crawler: " + j.Court + " " + j.Date.Format("2006-01-02"))

		path := conf.OutDir + "/" + j.Court + "/" + j.Date.Format("2006-01-02") + "/"
		if conf.OutMode == "fs" {
			os.MkdirAll(path, os.ModePerm)
		}

		for i, c := range j.Cases {
			index := i + 1
			caseHtml := crawlPage(client, baseUrl+c.CaseUrl, referer)
			histHtml := crawlPage(client, baseUrl+c.HistUrl, referer)

			if conf.OutMode == "fs" {
				ioutil.WriteFile(path+strconv.Itoa(index)+".html", caseHtml, os.ModePerm)
				ioutil.WriteFile(path+strconv.Itoa(index)+"-h.html", histHtml, os.ModePerm)
			} else {
				id := j.Court + j.Date.Format("20060102") + padI2S(index, 3)
				stmt, err := db.Prepare("INSERT INTO raw_data VALUES ($1, $2, $3, $4, $5, $6)")
				errHandler(err, "Error preparing db statement")
				_, err = stmt.Exec(id, j.Court[:3], j.Court[3:4], j.Date.Format("2006-01-02"), string(caseHtml), string(histHtml))
				errHandler(err, "Error inserting data into db: "+id)
				if err != nil {
					ioutil.WriteFile(conf.OutDir+"/"+id+".html", caseHtml, os.ModePerm)
					ioutil.WriteFile(conf.OutDir+"/"+id+"-h.html", histHtml, os.ModePerm)
				}
			}
			time.Sleep(time.Duration(rateLimit) * time.Millisecond)
		}

		log.Println("Crawler: " + j.Court + " " + j.Date.Format("2006-01-02") + " Complete")
	}
}

var wg sync.WaitGroup

func main() {
	// getting configs
	// [search, crawl, all]
	mode := os.Args[1]
	var conf Config
	_, err := toml.DecodeFile(os.Args[2], &conf)
	errHandler(err, "Error decoding config")

	// set logging
	l, err := os.OpenFile(conf.General.LogFile, os.O_RDWR|os.O_APPEND, 0660)
	errHandler(err, "Error creating log file: "+conf.General.LogFile)
	log.SetOutput(l)

	log.Println("started")

	// setup db if needed
	var db *sql.DB
	if mode != "search" && conf.Crawler.OutMode == "db" {
		db, err = sql.Open("postgres", "postgres://"+conf.Crawler.Login)
		errHandler(err, "Error opening db connection")

		err = db.Ping()
		errHandler(err, "Error pinging db")
	}

	// setup client for reuse
	client := &http.Client{}

	// start searching, if needed
	if mode == "search" || mode == "all" {
		searchWorker(client, conf.Searcher.InputFile, conf.Searcher.OutputFile, conf.General.RateLimit)
	}

	if mode == "crawl" || mode == "all" {
		jobs := make(chan caseList, 100000)
		for i := 0; i < conf.General.MaxThreads; i++ {
			wg.Add(1)
			go crawlerWorker(client, jobs, conf.Crawler, db, conf.General.RateLimit)
		}

		f, err := os.Open(conf.Crawler.InputFile)
		errHandler(err, "Error opening crawler input file")
		defer f.Close()
		d := json.NewDecoder(f)
		var todo []caseList
		err = d.Decode(&todo)
		errHandler(err, "Error decoding input json")

		for _, t := range todo {
			jobs <- t
		}

		for i := 0; i < conf.General.MaxThreads; i++ {
			jobs <- caseList{"exit", time.Now(), nil}
		}
	}

	wg.Wait()
}
