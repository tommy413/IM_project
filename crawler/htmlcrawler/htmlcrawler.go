package main

import (
	"database/sql"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/BurntSushi/toml"
	_ "github.com/lib/pq"
)

type Conf struct {
	RateLimit int
	BatchSize int
	LogFile   string
	Db        string
}

// handle errors
func errHandler(err error, msg string) {
	if err != nil {
		log.Println(msg)
		log.Print(err)
	}
}

// for each page download and save it
func worker(db *sql.DB, client *http.Client, conf Conf) bool {
	// set prepared statements
	// getWork.Query(conf.BatchSize)
	getWork, err := db.Prepare("UPDATE raw_urls SET inProgress = TRUE WHERE id IN (SELECT id FROM raw_urls WHERE inProgress = FALSE LIMIT $1) RETURNING *")
	errHandler(err, "Error preparing get work statement")
	// saveWork.Exec(id, caseUrl, histUrl, inprogress=0)
	saveWork, err := db.Prepare("INSERT INTO raw_html VALUES ($1, $2, $3)")
	errHandler(err, "Error preparing save work statement")
	// updateWork.Exec(id_from_getWork)
	updateWork, err := db.Prepare("DELETE FROM raw_urls WHERE id = $1")
	errHandler(err, "Error preparing update work statement")

	rows, err := getWork.Query(conf.BatchSize)
	errHandler(err, "Error querying db for work")
	notEmpty := false
	for rows.Next() {
		notEmpty = true
		var id, caseUrl, histUrl string
		var mod bool
		err = rows.Scan(&id, &caseUrl, &histUrl, &mod)
		errHandler(err, "Error scanning rows")
		log.Printf("Job received: %s \n", id)

		time.Sleep(time.Duration(conf.RateLimit) * time.Millisecond)
		caseHtml := []rune(string(crawlPage(client, caseUrl)))
		time.Sleep(time.Duration(conf.RateLimit) * time.Millisecond)
		histHtml := []rune(string(crawlPage(client, histUrl)))

		_, err = saveWork.Exec(id, string(caseHtml), string(histHtml))
		errHandler(err, "Error saving html to db: "+id)

		_, err = updateWork.Exec(id)
		errHandler(err, "Error updating raw_todo")
		log.Println("Job completed: " + id)
	}
	return notEmpty
}

func crawlPage(client *http.Client, urlpath string) []byte {
	baseUrl := "http://jirs.judicial.gov.tw/FJUD/"
	req, err := http.NewRequest("GET", baseUrl+urlpath, nil)
	errHandler(err, "Error creating crawl request")
	req.Header.Add("Referer", "http://jirs.judicial.gov.tw/FJUD/FJUDQRY02_1.aspx")

	res, err := client.Do(req)
	delay := 4
	for err != nil {
		log.Printf("Error executing crawl request, retrying in %d seconds\n", delay)
		log.Print(err)
		time.Sleep(time.Duration(delay) * time.Millisecond)
		if delay < 600 {
			delay = delay * 2
		}
		res, err = client.Do(req)
	}

	defer res.Body.Close()
	data, err := ioutil.ReadAll(res.Body)
	errHandler(err, "Error reading response")
	return data
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
