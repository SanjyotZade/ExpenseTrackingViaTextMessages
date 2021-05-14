
#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"
dt=$(date '+%d/%m/_%H:%M:%S');
echo "------------------------------------------------------" >> sms.log
echo $dt >> sms.log
#pkill -9 python
source /Users/sanjyotzade/anaconda3/bin/activate expenseTracking
nohup python -u run.py >> sms.log &
echo $! >> sms.log
#tail -f  sms.log