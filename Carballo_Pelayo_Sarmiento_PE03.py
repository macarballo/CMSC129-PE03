import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# Variables to store filenames and validation results
production_filename = "No file loaded"
parse_table_filename = "No file loaded"
is_production_loaded = False
is_parsetable_loaded = False

input_tokens_values = None
productions_values = None
parse_table_values = None


# Function to parse tokens using the loaded production and parse table
def parse_tokens_with_grammar(productions: dict, parse_table: dict):
    print(f"Productions: {productions}")
    print(f"Parse table: {parse_table}")

    # Get tokens from the input field and strip extra spaces
    input_tokens = tokens_entry.get().strip().split()

    # Show an error message if no tokens are provided
    if not input_tokens:
        messagebox.showerror("Error", "No input tokens provided!")
        return

    print(f"Parse tokens: {input_tokens}")

    stack = ["$", "E"]  # Initialize stack with end marker and start symbol
    input_buffer = input_tokens + ["$"]  # Append end marker to input tokens
    parsing_steps = []  # To store parsing steps
    is_valid = True  # Indicates if parsing is successful

    while stack:
        stack_top = stack[-1]
        current_input = input_buffer[0]
        current_stack = " ".join(stack)
        current_buffer = " ".join(input_buffer)

        # If stack top matches current input token
        if stack_top == current_input:
            stack.pop()
            input_buffer.pop(0)
            action = f"Match {stack_top}"
            print(action)

        elif stack_top in parse_table:  # Stack top is a non-terminal
            if current_input in parse_table[stack_top]:
                production_number = parse_table[stack_top][current_input]
                if production_number == "":
                    action = "Error: No rule found"
                    print(action)
                    is_valid = False
                    break
                else:
                    stack.pop()
                    production = productions[
                        int(production_number) - 1
                    ]  # Get production
                    rhs = production[2].split() if production[2] != "e" else []
                    stack.extend(reversed(rhs))  # Push production to stack
                    action = f"Output {production[1]} -> {production[2]}"
                    print(action)
            else:
                action = "Error: No matching terminal in parse table"
                print(action)
                is_valid = False
                break
        else:
            action = f"Error: Unexpected token {stack_top}"
            print(action)
            is_valid = False
            break

        # Log the step
        parsing_steps.append((current_stack, current_buffer, action))

    print(f"steps {parsing_steps}")
    print(f"is_valid {is_valid}")


# Function to load the productions from .prod file
def load_productions(file_path):
    productions = []
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            productions.append(row)
    return productions


# Function to load the parse table from .ptbl file
def load_parse_table(file_path):
    parse_table = {}
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)[1:]  # Skip the first column for non-terminals
        for row in reader:
            non_terminal = row[0]
            parse_table[non_terminal] = {
                headers[i]: row[i + 1] for i in range(len(headers))
            }
    return parse_table


# Function to load files and display content in the table
def load_file():
    global \
        production_filename, \
        parse_table_filename, \
        is_production_loaded, \
        is_parsetable_loaded
    global productions_values, parse_table_values

    # Prompt user to select a file
    file_path = filedialog.askopenfilename(
        filetypes=[("Production or Parse Table Files", "*.prod *.ptbl")]
    )

    # If no file is selected, exit the function
    if not file_path:
        return

    try:
        # Open and read the selected file
        with open(file_path, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            file_content = list(reader)

            # Determine whether it's a production file or parse table
            # Determine whether it's a production file or parse table
            if file_path.endswith(".prod"):
                production_filename = file_path.split("/")[-1]
                production_label.config(text=f"Productions: {production_filename}")
                display_content(production_table, file_content, ["ID", "NT", "P"])
                productions_values = load_productions(file_path)
                is_production_loaded = True

            elif file_path.endswith(".ptbl"):
                parse_table_filename = file_path.split("/")[-1]
                parsetable_label.config(text=f"Parse Table: {parse_table_filename}")
                display_content(parse_table, file_content, file_content[0])
                parse_table_values = load_parse_table(file_path)
                is_parsetable_loaded = True

            # Clear parsing result when a new file is loaded
            parsing_result_table.delete(*parsing_result_table.get_children())
            parsing_message_label.config(text="PARSING: Not yet parsed")

            # Enable the parse button if both files are loaded
            if is_production_loaded and is_parsetable_loaded:
                parse_button.config(state=tk.NORMAL)

            # Update the "LOADED" message area with the most recently loaded file
            loaded_file_label.config(text=f" {file_path.split('/')[-1]}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")


# Function to display content in a Treeview table with fixed column width
def display_content(table, content, columns):
    # Clear the existing columns before setting new ones
    table["columns"] = ()  # This clears the columns first

    table.config(columns=columns)

    # Clear any existing content in the table
    for row in table.get_children():
        table.delete(row)

    # Set fixed column width for each column
    fixed_width = 80  # Set a fixed width for each column (adjust as needed)
    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=fixed_width, stretch=tk.NO)

    # Insert new content
    for row in content:  # Include all rows, including the first one
        # Check if the row has the expected number of columns
        if len(row) == len(
            columns
        ):  # Ensure the number of columns in the row matches the table's columns
            table.insert("", "end", values=row)
        else:
            print(f"Skipping invalid row: {row}")


# Function to ask the user for the output filename and append the production filename
def get_output_filename():
    # Prompt user to specify the output file location
    outname = filedialog.asksaveasfilename(
        defaultextension=".prsd", filetypes=[("Parsed File", "*.prsd")]
    )

    # If no filename is selected, return None
    if not outname:
        return None

    # Append the production filename to the output file name
    return f"{outname}_{production_filename.split('.')[0]}.prsd"


# Initialize the main Tkinter window
root = tk.Tk()
root.title("Non-Recursive Predictive Parser")
root.state("zoomed")  # Start maximized


# Configure root grid to allow dynamic resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Frame for displaying Productions
production_frame = tk.LabelFrame(
    root, text="Productions", font=("Courier New", 12, "bold")
)
validation_result = tk.StringVar()
production_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

production_label = tk.Label(
    production_frame,
    text=f"Productions: {production_filename}",
    font=("Courier New", 12),
)
production_label.pack(anchor="w", padx=5, pady=5)

production_table = ttk.Treeview(production_frame, show="headings", height=10)
production_table.pack(expand=False, fill="both", padx=5, pady=5)
production_table["columns"] = ("ID", "NT", "P")
production_table.configure(style="Custom.Treeview")

# Frame for displaying Parse Table
parsetable_frame = tk.LabelFrame(
    root, text="Parse Table", font=("Courier New", 12, "bold")
)
parsetable_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

parsetable_label = tk.Label(
    parsetable_frame,
    text=f"Parse Table: {parse_table_filename}",
    font=("Courier New", 12),
)
parsetable_label.pack(anchor="w", padx=5, pady=5)

parse_table = ttk.Treeview(parsetable_frame, show="headings", height=10)
parse_table.pack(expand=False, fill="both", padx=5, pady=5)
parse_table["columns"] = ["Non-Terminals"]  # Initial column for non-terminals
parse_table.configure(style="Custom.Treeview")


# Load button for loading files
load_button = tk.Button(
    root,
    text="Load",
    command=load_file,
    font=("Courier New", 12, "bold"),
    bg="#20283E",
    fg="white",
)
load_button.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

# Frame for displaying loaded message
loaded_message_frame = tk.Frame(root)
loaded_message_frame.grid(row=2, column=0, columnspan=2, pady=15, padx=15, sticky="w")

loaded_label = tk.Label(
    loaded_message_frame, text="LOADED:", font=("Courier New", 12, "bold")
)
loaded_label.pack(side=tk.LEFT)

loaded_file_label = tk.Label(
    loaded_message_frame, text=" No file loaded", font=("Courier New", 12)
)
loaded_file_label.pack(side=tk.LEFT)

# Input Frame for Token String
input_frame = tk.Frame(root)
input_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tk.Label(input_frame, text="INPUT:", font=("Courier New", 12, "bold")).grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)

tokens_entry = tk.Entry(input_frame, font=("Courier New", 12), width=30)
tokens_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Parse button
parse_button = tk.Button(
    root,
    text="Parse",
    command=lambda: parse_tokens_with_grammar(productions_values, parse_table_values),
    font=("Courier New", 12, "bold"),
    bg="#2A72D2",
    fg="white",
    state=tk.DISABLED,
)
parse_button.grid(row=4, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")

# Frame for displaying parsing results
parsing_result_frame = tk.LabelFrame(
    root, text="Parsing Results", font=("Courier New", 12, "bold")
)
parsing_result_frame.grid(
    row=5, column=0, columnspan=2, padx=10, pady=15, sticky="nsew"
)

parsing_message_label = tk.Label(
    parsing_result_frame, text="PARSING: Not yet parsed", font=("Courier New", 12)
)
parsing_message_label.pack(anchor="w", padx=5, pady=5)

parsing_result_table = ttk.Treeview(parsing_result_frame, show="headings", height=10)
parsing_result_table.pack(expand=True, fill="both", padx=5, pady=5)

parsing_result_table["columns"] = ["Stack", "Input Buffer", "Action"]
parsing_result_table.column("Stack", anchor="center")
parsing_result_table.column("Input Buffer", anchor="center")
parsing_result_table.column("Action", anchor="center")
parsing_result_table.configure(style="Custom.Treeview")

# Start the Tkinter main loop
root.mainloop()
