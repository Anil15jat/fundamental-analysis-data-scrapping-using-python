package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/playwright-community/playwright-go"
	//"github.com/yogiis/golang-web-automation/helpers"
	// "github.com/go-delve/delve/pkg/config"
)

func main() {
	get_screener_data()
}

func get_screener_data() {
	// Create a Playwright instance
	pw, err := playwright.Run()
	if err != nil {
		fmt.Println("Failed to create Playwright instance:", err)
		return
	}
	defer pw.Stop()

	// Use Playwright's browser and context APIs
	browser, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
		Headless: playwright.Bool(false), // Set headless to true
	})
	if err != nil {
		fmt.Println("Failed to launch Chromium:", err)
		return
	}
	defer browser.Close()

	page, err := browser.NewPage()
	if err != nil {
		fmt.Println("Failed to create page:", err)
		return
	}
	defer page.Close()

	// Now you can interact with the page using Playwright
	page.Goto("https://screener.in")

	loginToWebsite(page, "https://www.screener.in/home/", "anil15jat@gmail.com", "0TrustTest")
	companyNameList := []string{"reliance", "titan", "mtartech", "itc"}
	sleepDuration := 5 * time.Second
	for _, companyName := range companyNameList {
		time.Sleep(sleepDuration)
		goToCompanyUrlScreen(page, companyName)
		companyDataMap := make(map[string]interface{})
		companyDataMap["company_name"] = getCompanyName(page)
		companyDataMap["about_company"] = getAboutCompany(page)
		companyDataMap["ratio"] = getCompanyRatios(page)
		companyDataMap["peer_comparison"] = getPeerComparison(page)
		companyDataMap["quarterly_result"] = getQuarterlyResults(page)
		companyDataMap["profit_and_loss"] = getProfitAndLoss(page)
		companyDataMap["balance_sheet"] = getBalanceSheet(page)
		companyDataMap["cash_flow"] = getCashFlows(page)
		companyDataMap["ratios"] = getRatios(page)
		companyDataMap["quarterly_shareholding_patterns"] = getShareholdingPatterns(page, "quarterly-shp")
		companyDataMap["profilt_loss_ranges_table_content"] = getProfiltLossRangesTableContent(page)
		// fmt.Println("Extracted content:", companyDataMap)
		// Generate the current date in YYYY-MM-DD format
		currentDate := time.Now().Format("2006-01-02")
		// filePath := fmt.Sprintf("/home/%s-%s.txt", strings.ToUpper(companyName), currentDate)
		dirPath := fmt.Sprintf("/Users/anilkj/Documents/screener/%s", strings.ToUpper(companyName))
		// Ensure the directory exists; create it if it doesn't
		if err := os.MkdirAll(dirPath, os.ModePerm); err != nil {
			fmt.Println("Error creating directory:", err)
		}
		filePath := fmt.Sprintf("%s/%s.txt", dirPath, currentDate)
		jsonData, err := json.MarshalIndent(companyDataMap, "", "  ")
		if err != nil {
			fmt.Println("Error marshaling JSON:", err)
		}
		// Write the JSON data to a text file
		err = ioutil.WriteFile(filePath, jsonData, 0644)
		if err != nil {
			fmt.Println("Error writing JSON to file:", err)
		}
	}
}

func goToCompanyUrlScreen(page playwright.Page, companyName string) {
	companyPageUrl := strings.Replace("https://screener.in/company/company_name_string/consolidated", "company_name_string", strings.ToUpper(companyName), 1)
	page.Goto(companyPageUrl)
}

func loginToWebsite(page playwright.Page, url, username, password string) {
	page.Goto(url)
	page.Click("//*//a[contains(@class,'button')][contains(@class,'account')][contains(@href,'login')]")
	page.Fill("//*//input[contains(@name,'username')]", username)
	page.Fill("//*//input[contains(@name,'password')]", password)
	page.Click("//*//button[contains(@type,'submit')]")
}

func getCompanyName(page playwright.Page) string {
	companyNameXpath := "//*//h1[contains(@class,'show-from-tablet-landscape')]"
	companyName, _ := page.Locator(companyNameXpath).InnerText()
	return companyName
}

func getAboutCompany(page playwright.Page) string {
	companyAboutReadMoreXpath := "//*//button[contains(normalize-space(text()),'Read More')]"
	page.Click(companyAboutReadMoreXpath)
	companyAboutContentXpath := "//*//div[contains(@class,'modal-content')]"
	companyAboutContent, _ := page.Locator(companyAboutContentXpath).InnerText()
	closeCompanyAboutXpath := "//*//div[contains(@class,'modal-header')]//button"
	page.Click(closeCompanyAboutXpath)
	return companyAboutContent
}

func getCompanyRatios(page playwright.Page) map[string][]string {
	ratioMap := make(map[string][]string)
	companyRatioEntryXpath := "//*//div[contains(@class,'company-ratio')]//ul[contains(@id,'top-ratios')]/li//span[contains(@class,'name')]"
	ratioNameXpath := companyRatioEntryXpath + "[normalize-space(text())='ratio_name_string']"
	ratioNumberXpath := ratioNameXpath + "/..//span//span[contains(@class,'number')]"
	ratioList, _ := page.QuerySelectorAll(companyRatioEntryXpath)

	for _, ratioElement := range ratioList {
		ratioName, _ := ratioElement.InnerText()
		ratioNumberList, _ := page.QuerySelectorAll(strings.Replace(ratioNumberXpath, "ratio_name_string", ratioName, 1))
		ratioNumbers := []string{}
		for _, ratioNumberElement := range ratioNumberList {
			ratioNumber, _ := ratioNumberElement.InnerText()
			ratioNumbers = append(ratioNumbers, ratioNumber)
		}
		ratioMap[ratioName] = ratioNumbers
	}
	return ratioMap
}

func getPeerComparison(page playwright.Page) map[string]interface{} {
	peerComparisonMap := make(map[string]interface{})
	peersTableXpath := "//*//section[contains(@id,'peers')]"
	sectorXpath := peersTableXpath + "//div//p"
	sectorDetails, _ := page.Locator(sectorXpath).InnerText()
	sectorPattern := regexp.MustCompile(`^\S+:\s+(?P<sector_name>\S+)\s+\S+:\s+(?P<industry_name>\S+)`)
	patternMatch := sectorPattern.FindStringSubmatch(sectorDetails)
	// fmt.Println(patternMatch)
	if len(patternMatch) > 0 {
		peerComparisonMap["sector"] = patternMatch[1]
		peerComparisonMap["industry"] = patternMatch[2]
	}
	peerTableDataXpath := peersTableXpath + "//*//table[contains(@class,'data-table')]/tbody/tr"
	rowElementList, _ := page.QuerySelectorAll(peerTableDataXpath)
	header := []string{}
	data := []interface{}{}
	for _, row := range rowElementList {
		rowText, _ := row.InnerText()
		cells := strings.Split(rowText, "\t")
		// Check if the row contains header data
		if strings.Contains(cells[0], "S.No.") {
			header = cells
		} else {
			data = append(data, cells)
		}
	}
	peerComparisonMap["header"] = header
	peerComparisonMap["data"] = data
	return peerComparisonMap
}

func getAllElementsText(page playwright.Page, elemXpath string) []string {
	textList := []string{}
	_, err := page.WaitForSelector(elemXpath)
	if err != nil {
		fmt.Println("Failed to wait for selector: %v\n", err)
		return textList
	}
	elementList, _ := page.QuerySelectorAll(elemXpath)
	for _, element := range elementList {
		InnerText, _ := element.InnerText()
		textList = append(textList, InnerText)
	}
	return textList
}

func getQuarterlyResults(page playwright.Page) map[string]interface{} {
	quarterlyResultMap := make(map[string]interface{})
	quarterlyResultTableXpath := "//*//section[contains(@id,'quarters')]"
	quarterlyResultHeaderXpath := quarterlyResultTableXpath + "//*//table//thead//tr"
	quarterlyResultDataXpath := quarterlyResultTableXpath + "//*//table[contains(@class,'data-table')]/tbody/tr"
	quarterlyResultMap["header"] = strings.Split(getAllElementsText(page, quarterlyResultHeaderXpath)[0], "\t")
	quarterlyResultDataList := []interface{}{}
	rowElementList, _ := page.QuerySelectorAll(quarterlyResultDataXpath)
	for _, row := range rowElementList {
		rowText, _ := row.InnerText()
		if !strings.Contains("Raw PDF", strings.Split(rowText, "\t")[0]) {
			quarterlyResultDataList = append(quarterlyResultDataList, strings.Split(rowText, "\t"))
		}
	}
	quarterlyResultMap["data"] = quarterlyResultDataList
	return quarterlyResultMap
}

func getProfitAndLoss(page playwright.Page) map[string]interface{} {
	profitAndLossMap := make(map[string]interface{})
	profitAndLossTableXpath := "//*//section[contains(@id,'profit-loss')]"
	profitAndLossHeaderXpath := profitAndLossTableXpath + "//*//table//thead//tr"
	profitAndLossDataXpath := profitAndLossTableXpath + "//*//table[contains(@class,'data-table')]/tbody/tr"
	profitAndLossMap["header"] = strings.Split(getAllElementsText(page, profitAndLossHeaderXpath)[0], "\t")
	rowElementList, _ := page.QuerySelectorAll(profitAndLossDataXpath)
	profitAndLossDataList := []interface{}{}
	for _, row := range rowElementList {
		rowText, _ := row.InnerText()
		if !strings.Contains("Raw PDF", strings.Split(rowText, "\t")[0]) {
			profitAndLossDataList = append(profitAndLossDataList, strings.Split(rowText, "\t"))
		}
	}
	profitAndLossMap["data"] = profitAndLossDataList
	return profitAndLossMap
}

func getBalanceSheet(page playwright.Page) map[string]interface{} {
	return getTableContent(page, "balance-sheet")
}

func getCashFlows(page playwright.Page) map[string]interface{} {
	return getTableContent(page, "cash-flow")
}

func getRatios(page playwright.Page) map[string]interface{} {
	return getTableContent(page, "ratios")
}

func getTableContent(page playwright.Page, id string) map[string]interface{} {
	resultMap := make(map[string]interface{})
	tableXpath := strings.Replace("//*//section[contains(@id,'id_string')]", "id_string", id, 1)
	headerXpath := tableXpath + "//*//table//thead//tr"
	dataXpath := tableXpath + "//*//table[contains(@class,'data-table')]/tbody/tr"
	resultMap["header"] = strings.Split(getAllElementsText(page, headerXpath)[0], "\t")
	rowElementList, _ := page.QuerySelectorAll(dataXpath)
	resultDataList := []interface{}{}
	for _, row := range rowElementList {
		rowText, _ := row.InnerText()
		resultDataList = append(resultDataList, strings.Split(rowText, "\t"))
	}
	resultMap["data"] = resultDataList
	return resultMap
}

func getShareholdingPatterns(page playwright.Page, patternType string) map[string]interface{} {
	resultMap := make(map[string]interface{})
	tableXpath := strings.Replace("//*//section[contains(@id,'shareholding')]//div[contains(@id,'pattern_type')]", "pattern_type", patternType, 1)
	headerXpath := tableXpath + "//*//table//thead//tr"
	dataXpath := tableXpath + "//*//table[contains(@class,'data-table')]/tbody/tr"
	resultMap["header"] = strings.Split(getAllElementsText(page, headerXpath)[0], "\t")
	rowElementList, _ := page.QuerySelectorAll(dataXpath)
	resultDataList := []interface{}{}
	for _, row := range rowElementList {
		rowText, _ := row.InnerText()
		resultDataList = append(resultDataList, strings.Split(rowText, "\t"))
	}
	resultMap["data"] = resultDataList
	return resultMap
}

func getProfiltLossRangesTableContent(page playwright.Page) map[string]interface{} {
	resultMap := make(map[string]interface{})
	tableXpath := "//*//section[contains(@id,'profit-loss')]//div//table[contains(@class,'ranges-table')]"
	headerXpath := tableXpath + "//tbody//tr//th"
	customHeaderXpath := tableXpath + "//tbody//tr//th[contains(text(),'header_name_string')]"
	customDataXpath := customHeaderXpath + "/../..//tr"
	headerNameList := getAllElementsText(page, headerXpath)
	for _, headerName := range headerNameList {
		rangeTableList := []interface{}{}
		rowElementList, _ := page.QuerySelectorAll(strings.Replace(customDataXpath, "header_name_string", headerName, 1))
		for _, row := range rowElementList {
			rowText, _ := row.InnerText()
			if !strings.Contains(headerName, strings.Split(rowText, "\t")[0]) {
				rangeTableList = append(rangeTableList, strings.Split(rowText, "\t"))
			}
		}
		resultMap[headerName] = rangeTableList
	}
	return resultMap
}
