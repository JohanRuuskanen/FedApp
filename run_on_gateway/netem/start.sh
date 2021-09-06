#!/bin/bash

get_network () {
    echo 'Please enter your target network: '
    networks=($(ifconfig -a -s | awk '$1 ~ /ens/' | awk '$1 != "ens3" {print $1}'))
#    networks=($(ifconfig | awk '{ print $1 }'))
    networks+=("Quit")
    select network in "${networks[@]}"
    do
        if [ $network == "Quit" ];
        then
	    exit 0
	fi

	if [ -z "$network" ];
	then
            echo "OK I will randomly choose a network for you."
            random=$((1 + RANDOM % ${#networks[@]}))
            echo $random
            network=${networks[random-1]}
        fi

        echo "You chose $network !"
	qdlist=($(tc qdisc | awk '($2 != "netem") {print $5}'))
	if [[ ${qdlist[*]} =~ $network ]]; then
	    echo "Add dev $network"
	    tc qdisc add dev $network root netem
	fi
        break
    done
}

get_action () {
    echo 'What do you want to do?'
    DESTROY="Destroy a cluster"
    DROP="Add packet loss to a cluster"
    DELAY="Add delay to a cluster"
    RESTORE="Restore a cluster"
    MAP="Read the delay matrix"
    actions=("$DESTROY" "$DROP" "$DELAY" "$RESTORE" "$MAP" "Do Nothing")
    select action in "${actions[@]}"
    do
        case $action in
            $DESTROY)
                echo "you chose to $action !"
                get_network
                break
                ;;
            $DROP)
                echo "you chose to $action !"
                get_network
                break
                ;;
            $DELAY)
                echo "you chose to $action !"
                get_network
                break
                ;;
            $RESTORE)
                echo "you chose to $action !"
                get_network
                break
                ;;
            $MAP)
                echo "you chose to $action !"
                break
                ;;
            "Do Nothing")
                exit 0
                ;;
            *) echo "Invalid option $REPLY";;
        esac
    done
}


echo "Hello!! I am chaos netem."
echo "I mess up the connection to your clusters"

get_action


#for net in "${networks[@]}"
#do
#   sudo tc qdisc add dev $net root netem
#done


if [ "$action" == "$DESTROY" ]; then
   tc qdisc change dev $network root netem loss 100%
fi

if [ "$action" == "$RESTORE" ]; then
   tc qdisc change dev $network root netem delay 0ms
fi

if [ "$action" == "$DROP" ]; then
    echo "Please input your desired loss rate (%). e.g. 30:"
    read loss

    if [[ $loss =~ ^[+-]?[0-9]+\.$ ]]; then
        echo "Invalid input."
        exit 0
    elif [ "$loss" -ge 100 ] && [ "$loss" -le 0 ]; then
        echo "loss should within the range (0,100)"
        exit 0
    else
        tc qdisc change dev $network root netem loss "$loss"%
    fi
fi

if [ "$action" == "$DELAY" ]; then
    echo "Please input your desired delay (ms):"
    read delay

    if [[ $loss =~ ^[+-]?[0-9]+\.$ ]]; then
        echo "Invalid input."
        exit 0
    elif [ "$delay" -lt 0 ]; then
        echo "delay should not be negative"
        exit 0
    else
	tc qdisc change dev $network root netem delay "$delay"ms
    fi
fi

if [ "$action" == "$MAP" ]; then
    networks=($(ifconfig -a -s | awk '$1 ~ /ens/' | awk '$1 != "ens3" {print $1}'))
    python3 /home/ubuntu/run_on_gateway/chaos_netem/network_mapping.py "${networks[@]}"
    echo "Delay added"
fi
