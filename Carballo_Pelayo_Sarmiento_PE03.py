import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# Function to load files and display content
def load_file():
    global production_filename, parse_table_filename, is_production_loaded, is_parsetable_loaded
    
    file_path = filedialog.askopenfilename(
        filetypes=[("Production or Parse Table Files", "*.prod *.ptbl")]
    )
    
    if not file_path:
        return
    
    try:
        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            file_content = list(reader)

            if file_path.endswith(".prod"):
                production_filename = file_path.split("/")[-1]
                production_label.config(text=f"Productions: {production_filename}")
                display_content(production_table, file_content, ["ID", "NT", "P"])
                is_production_loaded = True
                
            elif file_path.endswith(".ptbl"):
                parse_table_filename = file_path.split("/")[-1]
                parsetable_label.config(text=f"Parse Table: {parse_table_filename}")
                display_content(parse_table, file_content, file_content[0])
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
        if len(row) == len(columns):  # Ensure the number of columns in the row matches the table's columns
            table.insert("", "end", values=row)
        else:
            print(f"Skipping invalid row: {row}")

# Function to ask the user for the output filename and append the production filename
def get_output_filename():
    outname = filedialog.asksaveasfilename(defaultextension=".prsd", filetypes=[("Parsed File", "*.prsd")])
    if not outname:
        return None
    return f"{outname}_{production_filename.split('.')[0]}.prsd"

# Function to parse the tokens and save the results (Skeleton)
def parse_tokens():
    input_tokens = tokens_entry.get().strip().split()
    if not input_tokens:
        messagebox.showerror("Error", "No input tokens provided!")
        return

    # Skeleton parsing logic
    stack = ["S"]  # Start with the start symbol
    input_buffer = input_tokens
    actions = []
    parsing_steps = []
    is_valid = True  # Placeholder for actual validity check

    # Implement parsing logic here
    # Here is just a placeholder loop
    while stack and input_buffer:
        current_stack = " ".join(stack)
        current_input = " ".join(input_buffer)
        action = "shift"  # Example action (shift as default action)

        # Just an example action logic for demonstration
        if stack[-1] == input_buffer[0]:
            stack.pop()  # Simulate pop for matching token
            input_buffer.pop(0)  # Simulate moving the input buffer
            action = "match"
        else:
            action = "error"  # Simulate an error if no match
            is_valid = False  # Mark as invalid if an error occurs

        actions.append(action)
        parsing_steps.append((current_stack, current_input, action))

    # Display steps in the result table
    for row in parsing_result_table.get_children():
        parsing_result_table.delete(row)
    
    for step in parsing_steps:
        parsing_result_table.insert("", "end", values=step)

    # Save the parsing steps to an output file
    output_filename = get_output_filename()
    if output_filename:
        try:
            with open(output_filename, "w", newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Stack", "Input Buffer", "Action"])
                for step in parsing_steps:
                    writer.writerow(step)

            # After saving, update the parsing message label with the result and output filename
            if is_valid:
                parsing_message_label.config(text=f"PARSING: Valid. Please see {output_filename}")
            else:
                parsing_message_label.config(text=f"PARSING: Invalid. Please see {output_filename}")

            messagebox.showinfo("Success", f"Parsing steps saved to {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save parsing steps: {e}")

# Initialize main window
root = tk.Tk()
root.title("Non-Recursive Predictive Parser")
root.state("zoomed")  # Start maximized

# Configure root grid to allow dynamic resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# Variables to store filenames and validation results
production_filename = "No file loaded"
parse_table_filename = "No file loaded"
validation_result = tk.StringVar()
is_production_loaded = False
is_parsetable_loaded = False

# Frame for Productions
production_frame = tk.LabelFrame(root, text="Productions", font=("Courier New", 12, "bold"))
production_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

production_label = tk.Label(production_frame, text=f"Productions: {production_filename}", font=("Courier New", 12))
production_label.pack(anchor="w", padx=5, pady=5)

production_table = ttk.Treeview(production_frame, show="headings", height=10)
production_table.pack(expand=False, fill="both", padx=5, pady=5)
production_table["columns"] = ("ID", "NT", "P")
production_table.configure(style="Custom.Treeview")

# Frame for Parse Table
parsetable_frame = tk.LabelFrame(root, text="Parse Table", font=("Courier New", 12, "bold"))
parsetable_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

parsetable_label = tk.Label(parsetable_frame, text=f"Parse Table: {parse_table_filename}", font=("Courier New", 12))
parsetable_label.pack(anchor="w", padx=5, pady=5)

parse_table = ttk.Treeview(parsetable_frame, show="headings", height=10)
parse_table.pack(expand=False, fill="both", padx=5, pady=5)
parse_table["columns"] = ["Non-Terminals"]  # Initial column for non-terminals
parse_table.configure(style="Custom.Treeview")

# Load button below the production and parse table frames
load_button = tk.Button(root, text="Load", command=load_file, font=("Courier New", 12, "bold"), bg="#20283E", fg="white")
load_button.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

# Frame for displaying loaded message
loaded_message_frame = tk.Frame(root)
loaded_message_frame.grid(row=2, column=0, columnspan=2, pady=15, padx=15, sticky="w")

# "LOADED" label (bold)
loaded_label = tk.Label(loaded_message_frame, text="LOADED:", font=("Courier New", 12, "bold"))
loaded_label.pack(side=tk.LEFT)

# Rest of the message (normal)
loaded_file_label = tk.Label(loaded_message_frame, text=" No file loaded", font=("Courier New", 12))
loaded_file_label.pack(side=tk.LEFT)

# Input Frame for Token String (shifted down to row 3)
input_frame = tk.Frame(root)
input_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Label and entry field for tokens
tk.Label(input_frame, text="INPUT:", font=("Courier New", 12, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")

tokens_entry = tk.Entry(input_frame, font=("Courier New", 12))
tokens_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Ensure that the column for the entry field expands
input_frame.grid_columnconfigure(1, weight=1)

# Parse button (disabled initially) moved to row 4
parse_button = tk.Button(root, text="Parse", font=("Courier New", 12, "bold"), bg="#6AB187", fg="white", state=tk.DISABLED, command=parse_tokens)
parse_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

# Table to display the parsing results
parsing_result_frame = tk.LabelFrame(root, text="Parsing Result", font=("Courier New", 12, "bold"))
parsing_result_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

parsing_message_label = tk.Label(parsing_result_frame, text="PARSING: Not yet parsed", font=("Courier New", 12))
parsing_message_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

parsing_result_table = ttk.Treeview(parsing_result_frame, show="headings", height=10)
parsing_result_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

parsing_result_table["columns"] = ["Stack", "Input Buffer", "Action"]

parsing_result_frame.grid_rowconfigure(1, weight=1)
parsing_result_frame.grid_columnconfigure(0, weight=1)

# Run the Tkinter event loop
root.mainloop()