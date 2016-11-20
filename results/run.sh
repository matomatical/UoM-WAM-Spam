#!/bin/bash
t=300
while [ 1 ]
do
	echo "checking results..."
	python main.py
	echo "will check again in: $t (s)"
	sleep $t
done
echo "all done!"

# how to while loop:
#	https://www.cyberciti.biz/faq/shell-script-while-loop-examples/

# how to sleep:
# 	http://stackoverflow.com/a/21621163/5395650