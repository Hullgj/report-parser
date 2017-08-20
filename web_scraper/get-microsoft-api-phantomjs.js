"use strict";
var page = require('webpage').create();
var system = require('system');

if (system.args.length === 1) {
    console.log('Enter the Microsoft API to search for');
    phantom.exit(1);
} else {
    var API = system.args[1];
}

page.onConsoleMessage = function(msg) {
    console.log(msg);
};

// Check if jQuery is in the current directory, otherwise download it
var fs = require('fs');
var jquery_lib = "jquery.min.js";
if (!fs.exists(jquery_lib) || !fs.isFile(jquery_lib)) {
    console.log("Downloading JQuery as it is not in the current directory");
    jquery_lib = "https://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js"
}

page.open("https://social.msdn.microsoft.com/search/en-US/windows?query="+API+"&refinement=183", function(status) {
    if (status === "success") {
        page.includeJs(jquery_lib, function() {
            page.evaluate(function() {
                var link = $("div#SearchResultsDisplay div.SearchResult:first-child div.result a")[0].baseURI;
                console.log(link);

                var page = require('webpage').create();

                page.open(link, function (status) {
                    if (status === "success") {
                        page.evaluate(function () {
                            console.log('loaded ' + link);
                            var category = $('div#breadcrumbs a#breadcrumbDropDownButton');
                            console.log(category);
                        })
                    } else {
                      phantom.exit(1);
                    }
                })
            });
            phantom.exit(0);
        });
    } else {
      phantom.exit(1);
    }
});
