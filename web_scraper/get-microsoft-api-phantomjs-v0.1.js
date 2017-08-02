// From the argument search microsoft for the API name, get the first result
// then open that page and read the category from the breadcrump
// This allows all used APIs to be categorised for the RanDep Model

"use strict";
var RenderUrlsToFile,
    arrayOfAPIs,
    page = require('webpage').create(),
    system = require('system');

page.onConsoleMessage = function(msg) {
    console.log(msg);
};

// Check if jQuery is in the current directory, otherwise download it
var fs = require('fs');
var jqueryLib = "jquery.min.js"
if (!fs.exists(jqueryLib) || !fs.isFile(jqueryLib)) {
    console.log("Downloading JQuery as it is not in the current directory");
    jqueryLib = "https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"
}

RenderUrlsToFile = function(apis, callbackPerApi, callbackFinal) {
    var next, extract, validUrl, page, retrieve, apiIndex, webpage;
    apiIndex = 0;
    webpage = require("webpage")
    page = null;

    next = function(status, api) {
        page.close();
        callbackPerApi(status, api);
        return retrieve();
    }
    extract = function(url) {
        // var selector = "div#breadcrumbs a#breadcrumbDropDownButton",
        //     attr = "title";
        page.close();
        return page.open(url, function(status) {
            if (status === "success") {
                console.log("success opening " + url);
                return window.setTimeout((function() {
                    page.includeJs(jqueryLib, function() {
                        var domExtract;
                        page.evaluate(function() {
                            domExtract = document.querySelector("div#breadcrumbs a#breadcrumbDropDownButton").title;
                            console.log(domExtract);
                            if (domExtract === null) {
                                console.log("Error " + "selector" + " not found");
                            }
                        });
                    });
                }), 200);
            }
        });
    }
    validUrl = function(str) {
      var pattern = new RegExp('^(https?:\/\/)?'+ // protocol
        '((([a-z\d]([a-z\d-]*[a-z\d])*)\.)+[a-z]{2,}|'+ // domain name
        '((\d{1,3}\.){3}\d{1,3}))'+ // OR ip (v4) address
        '(\:\d+)?(\/[-a-z\d%_.~+]*)*'+ // port and path
        '(\?[;&a-z\d%_.~+=-]*)?'+ // query string
        '(\#[-a-z\d_]*)?$','i'); // fragment locater
      if(!pattern.test(str)) {
        console.log("Please enter a valid URL.");
        return false;
      } else {
        return true;
      }
    }
    retrieve = function() {
        var api;
        if (apis.length > 0) {
            api = apis.shift();
            apiIndex++;
            page = webpage.create();
            page.settings.userAgent = "Phantom.js bot";
            return page.open(
                "https://social.msdn.microsoft.com/search/en-US/windows?query="+
                api+"&refinement=183", function(status) {
                if (status === "success") {
                    // var selector = "div#SearchResultsDisplay div.SearchResult:first-child div.result a",
                    //     attr = "href";
                    var domExtract;
                    return window.setTimeout((function() {
                            // page.evaluate(function() {
                                console.log("trying to find " + "selector");
                                // page.includeJs(jqueryLib, function() {
                                    domExtract = document.querySelector("div#SearchResultsDisplay div.SearchResult:first-child div.result a").href;
                                console.log(domExtract);
                                // });
                            // });
                        if (domExtract === null) {
                            console.log("Error " + "selector" + " not found");
                        } else if (domExtract.match('^(https?:\/\/)?')) {
                            console.log("URL is valid ");
                            return extract(domExtract);
                        } else {
                            return next(status, api);
                        }
                    }), 200);
                } else {
                    return next(status, api);
                }
            });
        } else {
            return callbackFinal();
        }
    };
    return retrieve();
};

arrayOfAPIs = null;

if (system.args.length > 1) {
    arrayOfAPIs = Array.prototype.slice.call(system.args, 1);
} else {
    console.log("Enter the Microsoft API to search for\nUsing default settings");
    arrayOfAPIs = ["GetAdaptersAddresses", "GlobalMemoryStatusEx"];
}

RenderUrlsToFile(arrayOfAPIs, (function(status, url) {
    if (status !== "success") {
        return console.log("Unable to parse " + url);
    } else {
        return console.log("Rendered " + url);
    }
}), function() {
    return phantom.exit();
});
