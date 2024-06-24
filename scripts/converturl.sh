url="https://imsdb.com/scripts/Big-Lebowski,-The.html"
safe_url=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$url''', safe=':/'))")
echo $safe_url
