/*eslint strict:0*/
/*global CasperError, console, phantom, require*/

// we need to define the startsWith() prototype function as it is not yet supported by PhantomJS
if (!String.prototype.startsWith) {
    String.prototype.startsWith = function(searchString, position) {
        position = position || 0;
        return this.indexOf(searchString, position) === position;
    };
}

var links = [],
    category = [],
    description = [],
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
        api += " function";
        this.log(api, 'debug');
        casper.then(function () {
            this.fill('form[action="https://social.msdn.microsoft.com/search/windows"]', { query: api }, true);
        });
        casper.then(function () {
            // aggregate results for the search
            var link = casper.evaluate(getLinks);
            var link_str = "" + link;
            if (link_str.startsWith('http')) {
                casper.log("Concatenated: " + link, 'debug');
                links = links.concat(link);
            }
            else {
                casper.log("Link not found " + link, 'debug');
                links = links.concat("http://blank.org/");
            }
        })
    });
});

casper.then(function () {
    casper.each(links, function (casper, url) {
        casper.log("Links to parse: " + links, 'debug');
        casper.thenOpen(url, function () {
            casper.log("Opening url: " + url, 'debug');
            if(url.startsWith("https://msdn")) {
                if (this.exists('div#breadcrumbs a#breadcrumbDropDownButton')) {
                    this.log(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'), 'debug');
                    category.push(this.getElementAttribute('div#breadcrumbs a#breadcrumbDropDownButton', 'title'));
                } else {
                    category.push("cat_not_found");
                }
                if (this.exists('div#mainSection p:first-of-type'))
                    description.push(this.getElementInfo('div#mainSection p:first-of-type').text
                        .replace(/(?:\t\r\n|\r|\n|\t)/g, ''));
                else
                    description.push("the category was not found, try using the bing or google scrapers");
            }
            else {
                category.push("cat_not_found");
                description.push("the link and hence the category was not found, try using the bing or google scrapers");
            }
        });
    });
});

casper.run(function () {
    // echo and write the results in a JSON format
    var comma = ',',
        result = "";

    // casper.echo('{ ');
    fs.write('casperjs-results.txt', "{\n", 'w');

    category.forEach(function(cat, index) {

        if (index >= category.length - 1) {
            comma = '';
        }
        result = '"' + apis[index] + '": { "' + cat + '": { "link": "' + links[index] + '",' +
            '"description": "' + description[index] + '"' +
            '}}' + comma;
        casper.echo(result);
        fs.write('casperjs-results.txt', result + '\n', 'a');
    });

    // casper.echo(' }');
    fs.write('casperjs-results.txt', "}", 'a');
    this.exit();
});