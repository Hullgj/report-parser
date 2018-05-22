
#!/bin/bash
function checkErr {
	if [[ "$1" -ne 0 ]]; then
		if [[ -n "$3" ]]; then
			ERR="[!] Error: $3"
		else
			ERR="[!] Error: Unknown"
		fi
		echo -e "\e[31m"$ERR"\e[39m"
		if [[ "$4" == "exit" ]]; then
			while read pid; do
				sudo kill -9 pid
			done <$PID_SAVE
			rm $PID_SAVE
			deactivate > /dev/null 2>&1
			exit
		fi
	else
		if [[ -n "$2" ]]; then
			SUCCESS="[+] $2"
		else
			SUCCESS="[+] Success: Unknown"
		fi
		echo -e "\e[32m"$SUCCESS"\e[39m"	
	fi
}

function comment {
	echo "[-] $1"
}

PID_SAVE="start_dynamsis_save_pid.txt"
if [[ -f $PID_SAVE ]]; then
	comment "Deleting $PID_SAVE"
	rm $PID_SAVE
fi

function startCuckoo {
	source /home/gavin/cuckoo/bin/activate
	checkErr $? "VirtualEnvironment active" "Unable to enter Cuckoo VirtualEnvironment" 
	nohup cuckoo rooter --sudo -g gavin > start_dynamsis.log &
	echo $! >> $PID_SAVE
	checkErr $? "Rooter Started" "Unable to start rooter" "exit"
	nohup cuckoo web > /dev/null 2>&1 &
	echo $! >> $PID_SAVE
	checkErr $? "Webserver started on 127.0.0.1:8080" "Webserver not started. Port might be busy." 
	cuckoo -d
	checkErr $?
}

function iptablesAddRule {
	if [[ $1 -ne 0 ]]; then
		if [[ $2 = "sudo iptables"* ]]; then
			RULE=$2
		else
			checkErr 1 "" "iptablesAddRule missing parameter: firewall rule" "exit"
		fi
		comment "Adding rule: $RULE"
		MODE="-A"
		eval "${RULE/ -C / -A }"
	fi
}

function ufwAddRule {
	if [[ $# -ne 5 ]]; then
		checkErr 1 "" "ufwAddRule: called with insufficient arguments" "exit"
	fi
	PORT=$1
	PROTOCOL=$2
	INTERFACE=$3
	STATE=$4
	WHERE=$5
	UFW_STATUS=(`sudo ufw status | awk '/Status/ {print $2}'`)
	if [[ $UFW_STATUS == "inactive" ]]; then
		sudo ufw enable
	fi
	UFW_RULES=(`sudo ufw status | grep -i $PORT/$PROTOCOL.*$INTERFACE.*$STATE.*$WHERE`)
	if [[ $UFW_RULES ]]; then
		comment "ufw rule setup OK"
	else
		sudo ufw $STATE in on $INTERFACE to $WHERE port $PORT proto $PROTOCOL
	fi
}

function setFirewallRules {
	# These are set only for the current session. First we check then add if needed
	MODE="-C"
	RULES=(
		"sudo iptables -t nat $MODE POSTROUTING -o ens33 -s 192.168.56.0/24 -j MASQUERADE"
		"sudo iptables -P FORWARD DROP"
		"sudo iptables $MODE FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT"
		"sudo iptables $MODE FORWARD -s 192.168.56.0/24 -j ACCEPT"
		"sudo iptables $MODE FORWARD -s 192.168.56.0/24 -d 192.168.56.0/24 -j ACCEPT"
		"sudo iptables $MODE FORWARD -j LOG"
		"sudo iptables -t nat $MODE PREROUTING -d 192.168.56.1 -p udp --dport 53 -j REDIRECT --to-ports 5342"
		"sudo iptables -t nat $MODE PREROUTING -i vboxnet0 -j REDIRECT"
	)
	for rule in "${RULES[@]}"; do
		$rule > /dev/null 2>&1
		iptablesAddRule $? "$rule"
	done

	echo 1 | sudo tee -a /proc/sys/net/ipv4/ip_forward
	sudo sysctl -w net.ipv4.ip_forward=1

	ufwAddRule "5342" "udp" "vboxnet0" "allow" "any"
}

function startVirtualHost {
	# VirtualBox host only network interface vboxnet0 should be up on 192.168.56.1
	STATUS=(`VBoxManage list hostonlyifs | awk '/Status/ {print $2}'`)
	if [[ $STATUS == "Down" ]]; then
	 	sudo ifconfig vboxnet0 192.168.56.1
	 	checkErr $? "Virtual Host Started" "Unable to start Virtual Host" "exit"
	fi
}

function startINetSim {
	INETSIM=(`nohup sudo inetsim | grep failed &`)
	echo $! >> $PID_SAVE
	if [[ $INETSIM = *"failed"* ]]; then
		checkErr 1 "" "iNetSim has a failed protocol/port: $INETSIM" "exit"
	fi
}

setFirewallRules
startVirtualHost
startINetSim
startCuckoo