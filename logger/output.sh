#!/bin/bash

# Check if the group name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <node-group> [<teros-node>]"
  exit 1
fi

# Define the node group and optional teros node
NODE_GROUP="$1"
TEROS_NODE="$2"

# Get the list of nodes in the specified group
NODES=$(kubectl get nodes --selector=group=${NODE_GROUP} --no-headers -o custom-columns=NAME:.metadata.name)

# Display the node group header
echo "Node Group: ${NODE_GROUP}"

# If a specific Teros node is provided, fetch and display its data
if [ -n "$TEROS_NODE" ]; then
    echo ""

    TEROS_OUTPUT=$(kubectl exec -it $(kubectl get pods --no-headers -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName | grep ${TEROS_NODE} | awk '{print $1}') -- tail -n1 data/exp1-teros.log)
    
    # Extract and format the Teros data
    TEROS_TEMP=$(echo $TEROS_OUTPUT | jq -r '.data.temperature')
    TEROS_VWC=$(echo $TEROS_OUTPUT | jq -r '.data.volumetric_water_content')
    TEROS_EC=$(echo $TEROS_OUTPUT | jq -r '.data.electric_conductivity')
    TEROS_TIME=$(echo $TEROS_OUTPUT | jq -r '.data.poll_time' | xargs -I{} date -d @{} +"%H:%M:%S %d/%m/%Y")

    # Print the Teros results
    echo "Teros Output [last updated at ${TEROS_TIME}]:"
    echo "Volumetric Water Content: ${TEROS_VWC}"
    echo "Electrical Conductivity: ${TEROS_EC}"
    echo "Temperature: ${TEROS_TEMP}"
fi

# Iterate through each node in the group (excluding the specified Teros node if any)
for NODE in $NODES; do
        # Get the list of pods on the current node
        PODS=$(kubectl get pods --no-headers -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName | grep ${NODE} | awk '{print $1}')
        
        # Iterate through each pod
        for POD in $PODS; do
            # Execute the command to get the PCB data
            PCB_OUTPUT=$(kubectl exec -it ${POD} -- tail -n1 data/exp1-pcb.log)
            
            # Extract and format the PCB data
            PCB_VOLTAGE=$(echo $PCB_OUTPUT | jq -r '.data.voltage')
            PCB_VOLTAGE=$(printf "%.2f" $PCB_VOLTAGE)
            PCB_TIME=$(echo $PCB_OUTPUT | jq -r '.data.poll_time' | xargs -I{} date -d @{} +"%H:%M:%S %d/%m/%Y")
            
            # Print the results
            echo ""
            echo "Node: ${NODE}"
            echo "PCB Output [last updated at ${PCB_TIME}]:"
            echo "Voltage: ${PCB_VOLTAGE} V"
        done
done

