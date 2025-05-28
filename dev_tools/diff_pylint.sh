FILES="../orig/dtimer.pyw dtimer.pyw"

for F in $FILES
do
	pylint $F | sed 's/.*: //;s/.lines [0-9]*.//' | tee $F.pylint
done

diff -u ../orig/dtimer.pyw.pylint dtimer.pyw.pylint | tee t.dif | less