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

    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size,size)
    fill_value = 999
    w_matrix = np.full(shape,fill_value)

    # All elements where row == col should be zero
    # U==V -> W(u,v)==0
    for e in range(size):
        for n in range(size):
            w_matrix[e,n,n] = 0

    # Modify elements in w-matrix using "edge_delays" dictionary in circuit_info
    # Access using edge_name as key and edge_delay as the value. 
    # edge_name ends in two integers: first=row, second=col 
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        # First four characters are always the same, 'Edge'
        # Arrays start from 0. Row = (node-1) and Col = (node-1)
        i, j = map(int, edge_name[4:])
        for e in range(size):
            w_matrix[e,i-1,j-1] = edge_delay

    # Parameterized the algorithm by adding a 3rd dimension to my array
    # e represents the maximum number of edges considered in any given path
    for e in range(1,size):
        for r in range(size):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (w_matrix[e-1,r,i] + w_matrix[e-1,i,c]) < w_matrix[e,r,c]:
                            w_matrix[e,r,c] = (w_matrix[e-1,r,i] + w_matrix[e-1,i,c]) 
                        else:
                            w_matrix[e,r,c]=w_matrix[e,r,c]
    
    return w_matrix


def create_gpmatrix(circuit_info):
    """
    Create G-Prime Matrix
    
    Populate initial matrix using w'(e)=m*w(e)-d(u)
    """
    
    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size,size)
    fill_value = 999
    gp_matrix = np.full(shape,fill_value)

    # Initialize gp-matrix using edge_delays, node_delays and M 
    node_delay = circuit_info.get("node_delays")
    m_value = size * max(node_delay)
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        i, j = map(int, edge_name[4:])
        for e in range(size):
            gp_matrix[e,i-1,j-1] = m_value * edge_delay - node_delay[i-1]
 
    # Parameterized the algorithm by adding a 3rd dimension to my array
    # e represents the maximum number of edges considered in any given path
    for e in range(1,size):
        for r in range(size):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (gp_matrix[e-1,r,i] + gp_matrix[e-1,i,c]) < gp_matrix[e,r,c]:
                            gp_matrix[e,r,c] = (gp_matrix[e-1,r,i] + gp_matrix[e-1,i,c]) 
                        else:
                            gp_matrix[e,r,c]=gp_matrix[e,r,c]
    
    return gp_matrix


def create_dmatrix(circuit_info, w_matrix, gp_matrix):
    """
    Create D Matrix
    
    Populate matrix using D(u,v)=m*W(u,v)-G'(u,v)+d(v) 
    """
    
    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (999)
    # This default value represents no path between the two nodes
    size = circuit_info.get("total_nodes")
    shape = (size,size)

    # Initialize d-matrix 
    # All elements where row == col should be zero
    # U==V -> W(u,v)==0
    fill_value = 999
    d_matrix = np.full(shape,fill_value)

    node_delay = circuit_info.get("node_delays")
    m_value = size * max(node_delay)
    for i in range(size):
        for j in range(size):
            if i != j:
                d_matrix[i-1,j-1] = m_value * w_matrix[i-1,j-1] - gp_matrix[i-1,j-1] + node_delay[j-1]
            else:
                d_matrix[i-1,j-1] = node_delay[i-1]

    return d_matrix


def inequalities(circuit_info, w_matrix, d_matrix):
    """
    Create and Print Inequalities
    """
    
    size = circuit_info.get("total_nodes")
    c_value = circuit_info.get("max_clock_cycle")
    node_delay = circuit_info.get("node_delays")



    # Create a 3D array with 3 dimensions equal to the number of nodes
    # Populate this 3D array with a high number as initial value (999)
    # This array will be used to store and remove redundant inequalites
    # 1 Dimension will represent each new set of inequalites
    ineq_sets = c_value-max(node_delay)+3
    shape = (ineq_sets,size,size)
    fill_value = 999
    ineq_matrix = np.full(shape,fill_value)


    # Display the initial inequalites created from
    # the initial values of our node delays
    # edge_name ends in two integers: first=row, second=col 
    print("----------------------------------------")
    print(f"      Set of Initial Inequalities       ")
    print("----------------------------------------")
    for edge_name, edge_delay in circuit_info["edge_delays"].items():
    
        # First four characters are always the same, 'Edge'
        i, j = map(int, edge_name[4:])
        print(f"r({i}) - r({j}) <= {edge_delay}")
        ineq_matrix[0,i-1,j-1] = edge_delay


    # Display all inequalities created from starting c_value
    # Decrement c & repeat while c >= max node delay in our circuit
    g = 1
    while c_value >= max(node_delay):
        print("----------------------------------------")
        print(f" Set of Inequalities for C = {c_value}  ")
        print("----------------------------------------")
        for i in range(size):
            for j in range(size):
                if d_matrix[i,j] > c_value:
                    print(f"r({i+1}) - r({j+1}) <= {w_matrix[i,j]-1}")
                    ineq_matrix[g,i,j] = w_matrix[i,j]-1
                else:
                    continue
        g = g + 1
        c_value = c_value-1
    
    # Compare cells across one axis to reduce/remove redundant ineq
    for e in range(1,ineq_sets-1):
        for r in range(size):
            for c in range(size):
                if ineq_matrix[e,r,c] < ineq_matrix[ineq_sets-1,r,c]:
                    ineq_matrix[ineq_sets-1,r,c] = ineq_matrix[e,r,c] 
                else:
                    continue 
    

    # Display our reduced set of inequalities
    print("----------------------------------------")
    print(f"      Reduced Set of Inequalities       ")
    print("----------------------------------------")
    
    for k in range(size):
        for l in range(size):
            if ineq_matrix[ineq_sets-1,k,l] != 999:
                print(f"r({k+1}) - r({l+1}) <= {ineq_matrix[ineq_sets-1,k,l]}")
            else:
                continue


    return ineq_matrix

def constraint_graph(circuit_info,ineq_matrix):
    """
    Represent constraint graph with a matrix
    Constraint graph has one additional node
    Populate matrix from ineq_matrix but swap U <=> V
    """

    # Trying with only 1 dimensions equal to the number of nodes+1
    size = circuit_info.get("total_nodes")
    shape = (size,size+1,size)
    fill_value = 999
    constraint_matrix = np.full(shape,fill_value)


    # Fill all layers with cells from ineq_matrix, switching U and V
    # Fill the extra row with 0s
    for g in range(size):
 
        for n in range(size):
            constraint_matrix[g,size,n] = 0

        for i in range(size):
            for j in range(size):
                constraint_matrix[g,i,j] = ineq_matrix[j,i]

    # Parameterized the algorithm by adding a 3rd dimension to my array
    # g represents the each generation of matrix the algorithm creates
    for g in range(1,size):
        for r in range(size+1):
            for c in range(size):
                not_c = list(range(0,c))+list(range(c+1,size))
                for i in not_c:
                        if (constraint_matrix[g-1,r,i] + constraint_matrix[g-1,i,c]) < constraint_matrix[g,r,c]:
                            constraint_matrix[g,r,c] = (constraint_matrix[g-1,r,i] + constraint_matrix[g-1,i,c]) 
                        else:
                            constraint_matrix[g,r,c]=constraint_matrix[g,r,c]
    
    return constraint_matrix


   
# Run the thing and do the stuff 
if __name__ == "__main__":
    file_path_txt = 'example_input2.txt'
    parsed_info = parse_circuit_file(file_path_txt)
    last_gen = parsed_info.get("total_nodes")-1
    c_value = parsed_info.get("max_clock_cycle")
    node_delay = parsed_info.get("node_delays")
    reduced_ineq = c_value-max(node_delay)+2
    
    w_matrix = create_wmatrix(parsed_info)
    gp_matrix = create_gpmatrix(parsed_info)
    d_matrix = create_dmatrix(parsed_info,w_matrix[last_gen],gp_matrix[last_gen])
    
    # Will need to call inequalities matrix as well as contraing
    # matrix calculation here to help group items for readability

    
    print(parsed_info)
    
    print("----------------------------------------")
    print("                W Matrix                ")
    print("----------------------------------------")
    user_input = input("Would you like to see the generations?(y/n)")
    if user_input == 'y':
        print(w_matrix)
    elif user_input == 'n':
        print(w_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(w_matrix[last_gen])

    print("----------------------------------------")
    print("                G' Matrix               ")
    print("----------------------------------------")
    user_input = input("Would you like to see the generations?(y/n)")
    if user_input == 'y':
        print(gp_matrix)
    elif user_input == 'n':
        print(gp_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(gp_matrix[last_gen])

    print("----------------------------------------")
    print("                D Matrix                ")
    print("----------------------------------------")
    print(d_matrix)
    
    ineq_matrix = inequalities(parsed_info,w_matrix[last_gen],d_matrix)
    constraint_matrix = constraint_graph(parsed_info,ineq_matrix[reduced_ineq])
    
    print("----------------------------------------")
    print("           Constraint Matrix            ")
    print("----------------------------------------")
    user_input = input("Would you like to see the generations?(y/n)")
    if user_input == 'y':
        print(constraint_matrix)
    elif user_input == 'n':
        print(constraint_matrix[last_gen])
    else:
        print("Invalid response, only displaying final gen by default")
        print(constraint_matrix[last_gen]) 
    
    print("----------------------------------------")
    print("            Retiming Vector             ")
    print("----------------------------------------")
    print(constraint_matrix[last_gen][last_gen+1]) 
