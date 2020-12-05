"""
hmm_vis.py

This is a Python 3.x program that uses Tkinter to show a Hidden Markov Model
as a trellis diagram.  It contains some methods for partially animating the
display, including highlighting nodes, and labeling nodes and edges
with text and/or numeric information.

The methods in this module are intended to be called from another
program that implements an algorithm, such as the Forward Algorithm or
the Viterbi Algorithm.

Key methods to import from this module ...

show_entire_trellis -- lays out and shows a trellis diagram for an HMM.  The first
   argument is S: a list of strings naming the states of the state space.
   The second argument is a list of strings representing the observation sequence
   being processed.
   The width and height arguments set the size of the display, in pixel units.
   The variable has_initial_state should be set to True if the first element of S
   is a special initial state such as '<S>' and the last element of S is a special
   end state such as '<E>'.  This causes the layout to conform to that convention
   commonly used in NLP applications of HMMs.

highlight_node -- graphically highlights or unhighlights a node that has
   been previously drawn.  Works by modifying the properties of a Tkinter canvas
   oval object.

show_label_at_node -- draws some text at or near an existing node.

show_label_at_edge -- draws some text at or near the midpoint of an existing edge.

Other methods that might or might not be helpful in customizing the trellis display
are the following:

start_HMM_display  -- Opens a new window and starts drawing the HMM diagram.

show_next_time_step -- Draws another column of the trellis diagram, with
  interconnecting edges.

show_observation -- draws a textual label above a column of states.

hold -- pause the program so that the Tkinter window does not automatically close

At the end of this file there is a bunch of example calls to several of these
methods to show how they are used.  Running this file as a main program
demonstrates the capabilities.

S. Tanimoto, May 20, 2020.
"""

import tkinter as tk
DIAGRAM = None # global var. for the tkinter Canvas object
RAD = 10 # Radius of node circles on the screen, in pixels. Also used elsewhere,
 # as a unit for default spacing of some other things like margins.
Y_OBSERVATIONS = RAD

STATES_DX = None # horizontal spacing for nodes, computed automatically.
STATES_DY = None # Vertical spacing for nodes, computed automatically.
NEXT_STATE_X = None # Where horizontally to put the next column of states.
FIRST_STATE_X = None # Horizontal coordinate of the first column of states.
FIRST_STATE_Y = None # Vertical coordinate of the first state.
LAST_STATE_X = None # Horizontal coordinate of the last column of states.
LAST_STATE_Y = None # Vertical coordinate of the last state.
NODE_COORDS_CACHE = {}
LAYER_NO = None # Counts the time steps drawn so far.
X_VALUES = [] # Somewhat redundant with NODE_COORDS_CACHE, but holds x coords only
NODE_ITEMS = {} # Stores the circle canvas objects for poss. highlighting.
EDGE_ITEMS = {} # Stores the line objects for poss. highlighting.

def show_edge(x1,y1,x2,y2,starting_level,state1_string,state2_string,label='',dx=0,dy=0,color='black',rad=10):
    # Adds a graph edge to the canvas. Called by start_HMM_display,
    # show_initial_state, and show_next_time_step.
    line = DIAGRAM.create_line(x1,y1,x2,y2,fill=color)
    if label != '':
        x = int(0.5*(x1+x2)+dx)
        y = int(0.5*(y1+y2)+dy)
        DIAGRAM.create_text(x,y,text=label,fill=color)
    try:
        EDGE_ITEMS[(starting_level, state1_string, state2_string)]=line # Save canvas object for later access.
    except:
        print("Could not save line canvas item in show_edge.")
    return line # Return value only needed if an app will need to
    # later modify or delete the edge.

def show_node(x1,y1,rad,label='',dx=0,dy=0,color='light gray', outline='dark red'):
    node = DIAGRAM.create_oval(x1-rad,y1-rad,x1+rad,y1+rad,fill=color,outline=outline)
    if label != '':
        x=x1+dx
        y=y1+dy
        DIAGRAM.create_text(x,y,text=label,fill='black')
    try:
        NODE_ITEMS[(LAYER_NO, label)]=node # Save canvas object for later access.
    except:
        print("Could not save oval canvas item in show_node.")
    return node # This return value should not normally be needed, but is
    # returned for consistency with other methods here.

def start_HMM_display(S, expected_N, width=5000, height=5000,
                      has_initial_state=True):
    '''Call this before calling show_next_time_step.
    S is the full set of states, including <S> and <E> special states,
    which must be at the beginning of S and end of S, respectively.
    However, these special states are not required.
    If not using them, set has_initial_state to False.
    expected_N is the number of columns to lay out.
    '''
    global DIAGRAM, STATES_DX, STATES_DY, NEXT_STATE_X
    global FIRST_STATE_X, LAST_STATE_X, FIRST_STATE_Y, LAST_STATE_Y
    global LAYER_NO

    # Set up a Tkinter window and canvas.
    window = tk.Tk()
    window.title("A Trellis Diagram from hmm_vis.py")
    DIAGRAM = tk.Canvas(width=width, height=height)
    DIAGRAM.pack()

    # Compute some layout parameters, and initialize data structures.
    LAYER_NO = 0
    FIRST_STATE_X=3*RAD
    LAST_STATE_X = width-3*RAD
    FIRST_STATE_Y=5*RAD # Leave enough space for some labels.
    LAST_STATE_Y=height-3*RAD
    if has_initial_state:
        Sprime = S[1:-1]
        expected_N += 1
    else:
        Sprime = S
    STATES_DX = int((LAST_STATE_X - FIRST_STATE_X)/expected_N)
    STATES_DY = int((LAST_STATE_Y - FIRST_STATE_Y)/(len(Sprime)-1))
    NEXT_STATE_X = FIRST_STATE_X
    if has_initial_state:
        # draw node half-way down 1st column
        show_initial_state(Sprime, S[0])

def show_initial_state(Sprime, s0):
    '''Assumes there is a single starting state, and that it is
     the first element of list S.'''
    global FIRST_STATE_X, FIRST_STATE_Y, LAST_STATE_Y, STATES_DX, STATES_DY
    global NEXT_STATE_X, RAD, X_VALUES, LAYER_NO
    x1 = FIRST_STATE_X
    y1 = int((FIRST_STATE_Y + LAST_STATE_Y)/2)
    # draw outgoing edges
    x2 = x1 + STATES_DX
    y2 = FIRST_STATE_Y
    for i in range(len(Sprime)):
        show_edge(x1, y1, x2, y2, LAYER_NO, s0, Sprime[i])
        y2 += STATES_DY
    show_node(x1, y1, RAD, label=s0)
    cache_coords((0, s0), x1, y1) # Save coordinates to facilitate later
    # displays of textual labels, etc.
    NEXT_STATE_X += STATES_DX
    LAYER_NO += 1
    X_VALUES = [FIRST_STATE_X, NEXT_STATE_X]

def cache_coords(node_key, x, y):
    '''Save coordinates of each node on the screen, for easy
    repainting, or adding text labels, as an algorithm runs.'''
    NODE_COORDS_CACHE[node_key] = (x,y)

def get_coords(layer_no, state_string):
    try:
        (x,y) = NODE_COORDS_CACHE[(layer_no, state_string)]
    except:
        print("No coordinates stored for layer no ", layer_no, " and state string ",state_string)
        return (30,30) # Allows execution to continue, but graphics might pile up here.
    return (x,y)


def show_next_time_step(S, first=False, last=False, has_end_state=False):
    '''Draw a column of states and the edges leading out from them.
     But if last is True, don't draw outgoing edges, except
     if has_end_state is also True, and then draw special outgoing
     edges to a single end state.
     If first is True, currently also skips drawing the edges,
     but this may be a redundant option.
     '''
    global NEXT_STATE_X, LAYER_NO
    y = FIRST_STATE_Y
    x1 = NEXT_STATE_X
    x2 = x1 + STATES_DX
    if has_end_state:
        Sprime = S[1:-1]
    else:
        Sprime = S
    if not first and not last:
        y1 = y
        for i in range(len(Sprime)):
            y2 = y
            for j in range(len(Sprime)):
                show_edge(x1, y1, x2, y2, LAYER_NO, Sprime[i], Sprime[j])
                y2 += STATES_DY
            y1 += STATES_DY
    if last:
        if has_end_state:
            y1 = y
            y2 = int((FIRST_STATE_Y + LAST_STATE_Y)/2)
            for i in range(len(Sprime)):
                show_edge(x1, y1, x2, y2, LAYER_NO, Sprime[i], S[-1])
                y1 += STATES_DY
            show_node(x2,y2, RAD, label=S[-1])
            cache_coords((LAYER_NO+1, S[-1]), x2, y2)

    for i in range(len(Sprime)):
        show_node(x1, y, RAD, label=Sprime[i])
        cache_coords((LAYER_NO, Sprime[i]), x1, y)# Save coordinates to
        #  facilitate later displays of textual labels, etc.
        y += STATES_DY
    NEXT_STATE_X += STATES_DX
    X_VALUES.append(NEXT_STATE_X)
    LAYER_NO += 1

def show_observation(layer_no, text):
    # Add a textual label above a column of states.
    x = X_VALUES[layer_no]
    y = Y_OBSERVATIONS
    label = DIAGRAM.create_text(x, y, text=text)
    return label # Returned in case an application needs a handle to
       # delete or modify this canvas object later.

def show_entire_trellis(S, observation_sequence, width=1800, height=1000, has_initial_state=False):
    # Display all basic elements of a trellis diagram for a given HMM.
    # This includes nodes, edges, node labels (with state names), and an observation sequence.
    # The number of time steps shown depends on the observation sequence length.
    n_expected = len(observation_sequence)
    start_HMM_display(S, n_expected, width=width, height=height, has_initial_state=True)
    for level in range(n_expected-1):
        show_next_time_step(S, has_end_state=True)
    show_next_time_step(S, last=True, has_end_state=True)
    for i in range(1, n_expected+1):
        show_observation(i, observation_sequence[i-1])

def show_label_at_node(layer_no, state_string, text, dx=0, dy=0, color='black'):
    # Add a textual label at or near a node.
    (x,y) = get_coords(layer_no, state_string)
    label = DIAGRAM.create_text(x+dx, y+dy, text=text, fill=color)
    return label # Returned in case an application needs a handle to
       # delete or modify this canvas object later.

def show_label_at_edge(layer_no, tail_state_string, head_state_string, text, dx=0, dy=0, color='black'):
    # Add a textual label at or near the midpoint of an edge.
    (x1,y1) = get_coords(layer_no, tail_state_string)
    (x2,y2) = get_coords(layer_no+1, head_state_string)
    xm = int((x1+x2)/2); ym = int((y1+y2)/2)
    label = DIAGRAM.create_text(xm+dx, ym+dy, text=text, fill=color)
    return label # Returned in case an application needs a handle to
       # delete or modify this canvas object later.

def highlight_node(layer_no, state_string, highlight=True):
    '''Thicken the outline of the node, except if highlight is False,
     undo any highlighting.'''
    node = NODE_ITEMS[(layer_no, state_string)]
    if highlight:
        DIAGRAM.itemconfig(node, width=6)
    else:
        DIAGRAM.itemconfig(node, width=1)
    return node # Returned just in case an application wants to do anything
    # else with the canvas object, such as recolor it, etc.

def highlight_edge(layer_no, state_string1, state_string2, highlight=True):
    '''Thicken the edge, except if highlight is False, undo any highlighting.
    The edge is specified by its starting level number, the state it starts
    at (state_string1, and the state it ends at (state_string2).'''
    edge = EDGE_ITEMS[(layer_no, state_string1, state_string2)]
    if highlight:
        DIAGRAM.itemconfig(edge, width=4)
    else:
        DIAGRAM.itemconfig(edge, width=1)
    return edge # Returned just in case an application wants to do anything
    # else with the canvas object, such as recolor it, etc.

def hold():
    '''Block so the Tkinter display remains active'''
    tk.mainloop()

S = ['<S>','N','M','V','<E>'] # Toy example, for "unit" test here.
if __name__=='__main__':
    # Demonstration of sample calls, setting up the display of the
    # example HMM at https://www.youtube.com/watch?v=mHEKZ8jv2SY
    # Some of the numbers here are meaningless, just showing the graphical
    # functionality and calling patterns.
    start_HMM_display(S, 4, has_initial_state=True)
    show_next_time_step(S, has_end_state=True)
    show_label_at_edge(0, '<S>', 'N', '3/4', dx=-RAD/2, dy=-RAD, color='purple')
    show_observation(1,'Jane')
    show_next_time_step(S, has_end_state=True)
    show_observation(2,'will')
    show_next_time_step(S, has_end_state=True)
    show_observation(3,'spot')
    show_next_time_step(S, last=True, has_end_state=True)
    show_observation(4,'Will')
    show_label_at_node(2,'V', '0.15', dy=1.5*RAD, color='red')
    show_label_at_node(1,'N', '0.201', dx=-2*RAD,dy=-10, color='purple')
    highlight_node(2, 'M')
    highlight_node(4, 'N')
    highlight_node(2, 'M', False)
    highlight_edge(0, '<S>', 'V')
    hold()
    # Another possibility is to call this method:
    # show_entire_trellis(S, ['Jane','will','spot','Will'],800,500,True)
