
#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
dt=$(date '+%d/%m/_%H:%M:%S');
echo "------------------------------------------------------" >> sms.log
echo $dt >> sms.log
#pkill -9 python
#source /Users/sanjyotzade/anaconda3/bin/activate expenseTracking
sudo -H -u sj-jetson-1 nohup /usr/bin/python3 -u run.py True>> sms.log  2>&1 &
echo $! >> sms.log
#tail -f  sms.log
