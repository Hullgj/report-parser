/*eslint strict:0*/
/*global CasperError, console, phantom, require*/

var links = [],
    category = [],
    apis = null,
    casper = require("casper").create({
        verbose: false,
        logLevel: "debug"
    }),
    fs = require('fs');

if (casper.cli.args.length === 0 && Object.keys(casper.cli.options).length === 0) {
    casper.log("Enter the Microsoft API to search for\nUsing default settings", 'error');
    apis = ["GetAdaptersAddresses", "GlobalMemoryStatusEx", "GetAddrInfoW"];
} else {
    apis = Array.prototype.slice.call(casper.cli.args, 0);
}

casper.cli.drop("cli");
casper.cli.drop("casper-path");

if (casper.cli.args.length === 0 && Object.keys(casper.cli.options).length === 0) {
    casper.echo("No arg nor option passed").exit();
}

function getLinks() {
    // var links = document.querySelectorAll("div#SearchResultsDisplay div.SearchResult:first-child div.result a");
    // var links = document.querySelectorAll("h3.r a");
    var links = document.querySelectorAll("ol#b_results li:first-child h2 a");
    return Array.prototype.map.call(links, function(e) {
        try {
            // google handles redirects hrefs to some script of theirs
            // return (/url\?q=(.*)&sa=U/).exec(e.getAttribute("href"))[1];q=$API
            // return (/url\?query=(.*)&refinement=183/).exec(e.getAttribute("href"))[1];
            return (/url\?q=(.*)/).exec(e.getAttribute("href"))[1];
        } catch(err) {
            return e.getAttribute("href");
        }
    });
}

// casper.start("http://google.com/", function () {
// casper.start("https://social.msdn.microsoft.com/search/en-US/windows/");
casper.start("http://www.bing.com/");
// casper.start("https://social.msdn.microsoft.com/search/en-US/windows/", function () {
// search query using form
// this.fill('form[action="https://social.msdn.microsoft.com/search/windows"]', { query: apis[0] }, true);
// });

casper.then(function () {
    // aggregate results for the initial search
    links = this.evaluate(getLinks);
    casper.each(apis, function (casper, api) {
        this.log(api, 'debug');
        casper.then(function () {
            this.fill('form[action="/search"]', { q: api }, true);
        });
        casper.then(function () {
            // aggregate results for the search
            links = links.concat(casper.evaluate(getLinks));
        })
    });
});
casper.then(function () {
    // open the links found in search and get the category name from the breadcrumb of the web page
    casper.each(links, function (casper, url) {
        casper.thenOpen(url, function () {
            this.log(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'), 'debug');
            category.push(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'));
        });
    });
});

casper.run(function () {
    // echo and write the results in a JSON format
    var comma = ',',
        result = "";

    casper.echo('{ ');
    fs.write('casperjs-results.txt', "{\n", 'w');

    category.forEach(function(cat, index) {

        if (index >= category.length - 1) {
            comma = '';
        }
        result = '"' + cat + '": { "' + apis[index] + '": { "link": "' + links[index] + '"}}' + comma;
        casper.echo(result);
        fs.write('casperjs-results.txt', result + '\n', 'a');
    });

    casper.echo(' }');
    fs.write('casperjs-results.txt', "}", 'a');
    this.exit();
});