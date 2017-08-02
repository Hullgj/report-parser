/*eslint strict:0*/
/*global CasperError, console, phantom, require*/

var links = [],
    category = [],
    apis = null,
    casper = require("casper").create({
        verbose: false,
        logLevel: "debug"
    }),
    system = require('system');

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
    // var links = document.querySelectorAll("h3.r a");
    var links = document.querySelectorAll("div#SearchResultsDisplay div.SearchResult:first-child div.result a");
    return Array.prototype.map.call(links, function(e) {
        try {
            // google handles redirects hrefs to some script of theirs
            // return (/url\?q=(.*)&sa=U/).exec(e.getAttribute("href"))[1];
            return (/url\?query=(.*)&refinement=183/).exec(e.getAttribute("href"))[1];
        } catch(err) {
            return e.getAttribute("href");
        }
    });
}

// casper.start("http://google.com/", function () {
casper.start("https://social.msdn.microsoft.com/search/en-US/windows/");
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
            this.fill('form[action="https://social.msdn.microsoft.com/search/windows"]', { query: api }, true);
        });
        casper.then(function () {
            // aggregate results for the search
            links = links.concat(casper.evaluate(getLinks));
        })
    });
});

casper.then(function () {
    casper.each(links, function (casper, url) {
        casper.thenOpen(url, function () {
            this.log(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'), 'debug');
            category.push(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'));
        });
    });
});

casper.run(function () {
    // echo results in some pretty fashion
    this.echo(links.length + " links found:");
    this.log(" - " + links.join("\n - "), 'debug');
    category.forEach(function(element, index) {
        casper.echo(index + '. ' + element + ' -> ' + apis[index] + ' @ ' + links[index]);
    });
    this.exit();
});