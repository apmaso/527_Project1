
import numpy as np

def parse_circuit_file(file_path):
    """
    Parse the circuit file and extract relevant information.
    
    Returns dictionary with parsed information.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Dictionary to hold circuit information
    circuit_info = {
        "total_nodes": 0,
        "node_delays": [],
        "edge_delays": {},
        "max_clock_cycle": 0
    }

    for line in lines:
        # Ignore comments and empty lines
        if line.startswith('//') or line.strip() == '':
            continue

        # Split the line into key and value
        key, value = line.split('=')
        value = value.strip()  # Remove any leading/trailing whitespace

        if key == 'TotalNodes':
            circuit_info["total_nodes"] = int(value)
        elif key == 'NodeDelays':
            # Split the delays and convert them to integers
            circuit_info["node_delays"] = list(map(int, value.split(',')))
        elif key == 'MaxClockCycle':
            circuit_info["max_clock_cycle"] = int(value)
        else:
            # If key doesn't match any of of the options above, this must
            # be an edge delay entry. Parse the edge's name and delay value
            edge_name = key
            edge_delay = int(value)
            circuit_info["edge_delays"][edge_name] = edge_delay

    return circuit_info

def create_wmatrix(circuit_info):
    """
    Create initial W Matrix
    
    Populate matrix with edge weights from circuit info
    """

    # Create a 2D, square array with dimensions equal to the number of nodes
    # Populate this matrix with a high number as initial_value
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size, size)
    fill_value = 999
    w_matrix = np.full(shape,fill_value)

    # All elements where row == col should be zero
    # U==V -> W(u,v)==0
    for n in range(size):
        w_matrix[n, n] = 0

    # Modify elements in w-matrix using "edge_delays" dictionary in circuit_info
    # Access using edge_name as key and edge_delay as the value. 
    # edge_name ends in two integers: first=row, second=col 
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        # First four characters are always the same, 'Edge'
        i, j = map(int, edge_name[4:])
        # Arrays start from 0. Row = (node-1) and Col = (node-1)
        w_matrix[i-1, j-1] = edge_delay

    # Look at paths with 2 edges first... baby steps
    # Just to get the idea of how to implement... 
    for r in range(size):
        for c in range(size):
            not_c = list(range(0,c))+list(range(c+1,size))
            for i in not_c:
                if (w_matrix[r,i] + w_matrix[i,c]) < w_matrix[r,c]:
                    w_matrix[r,c]=(w_matrix[r,i]+w_matrix[i,c])
                else:
                    w_matrix[r,c]=w_matrix[r,c]

    # Look at paths with 3 edges next... baby steps
    # Just to get the idea of how to implement... 
    for r in range(size):
        for c in range(size):
            not_c = list(range(0,c))+list(range(c+1,size))
            for i in not_c:
                for j in not_c:
                    if (w_matrix[r,i] + w_matrix[i,j] + w_matrix[j,c]) < w_matrix[r,c]:
                        w_matrix[r,c] = (w_matrix[r,i] + w_matrix[i,j] + w_matrix[j,c]) 
                    else:
                        w_matrix[r,c]=w_matrix[r,c]


    return w_matrix



# Bolierplate
if __name__ == "__main__":
    file_path_txt = 'example_input.txt'
    parsed_info = parse_circuit_file(file_path_txt)
    w_matrix = create_wmatrix(parsed_info)
    print(parsed_info)
    print(w_matrix)
