cd /root/WillCallAlertSystem/
find logs -atime 20 -name '*.out' -print -exec /bin/rm {} \;
python main.py > logs/$$.out 2>&1
