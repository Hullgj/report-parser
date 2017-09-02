#!/bin/bash

for API in "$@"
do
    BING=`curl -s http://www.bing.com/search?q=$API |
    pup 'ol#b_results li:first-child h2 a attr{href}'`

    CATEGORY=`curl -s $BING |
    pup 'div#breadcrumbs a#breadcrumbDropDownButton attr{title}'`

    printf '"%s": {"%s": {"link": "%s"}}' "$CATEGORY" "$API" "$BING"
done
