cd /root/WillCallAlertSystem/
find logs \! -mtime 30 -name '*.out' -print -exec /bin/rm {} \;
python main.py > logs/$$.out 2>&1
