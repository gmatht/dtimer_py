set -e
FILES="*.py *.pyw *.md"
grep -e '[[:space:]]$' $FILES
