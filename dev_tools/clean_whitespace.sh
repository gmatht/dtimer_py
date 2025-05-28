set -e
FILES="*.py *.pyw *.md"
mkdir -p bak
zip bak/`date +%s%3N`.zip $FILES
for F in $FILES
do
	sed -i 's/[ \t\r]*$//' $F
done
