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

            # Enable the parse button if both files are loaded
            if is_production_loaded and is_parsetable_loaded:
                parse_button.config(state=tk.NORMAL)
            
            # Update the "LOADED" message area with the most recently loaded file
            loaded_file_label.config(text=f" {file_path.split('/')[-1]}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")

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

# Function to display content in a Treeview table with fixed column width
def display_content(table, content, columns):
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
    for row in content[1:]:  # Skipping header row if present
        table.insert("", "end", values=row)

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
load_button = tk.Button(root, text="Load", command=load_file, font=("Courier New", 12, "bold"), bg="#4CAF50", fg="white")
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
parse_button = tk.Button(root, text="Parse", font=("Courier New", 12, "bold"), bg="#008CBA", fg="white", state=tk.DISABLED, command=lambda: parse_tokens())
parse_button.grid(row=4, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

# Frame to hold the parsing message and result table moved to row 5
parsing_result_frame = tk.Frame(root)
parsing_result_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Message area for the parsing result
parsing_message_label = tk.Label(parsing_result_frame, text="PARSING: Not yet parsed", font=("Courier New", 12))
parsing_message_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

# Parsing result table (initially empty)
parsing_result_table = ttk.Treeview(parsing_result_frame, show="headings", height=10)
parsing_result_table.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
parsing_result_table["columns"] = ["Step", "Action", "Stack", "Input"]  # Example columns for parsing results
parsing_result_table.configure(style="Custom.Treeview")

# Function to parse tokens based on the loaded parse table and productions
def parse_tokens():
    tokens = tokens_entry.get().strip().split()  # Example of getting tokens from input
    
    # Parse message
    parsing_message_label.config(text="PARSING: Valid. Please see test_rules.prsd.")
    
    # Placeholder for parsing result (you'll replace this with actual parsing logic)
    parsing_result = [
        ("Step 1", "Action 1", "Stack 1", "Input 1"),
        ("Step 2", "Action 2", "Stack 2", "Input 2")
    ]
    
    # Clear the existing table and insert parsing results
    for row in parsing_result_table.get_children():
        parsing_result_table.delete(row)
    
    for row in parsing_result:
        parsing_result_table.insert("", "end", values=row)
    
    # Example: Saving result to a file
    with open("test_rules.prsd", "w") as file:
        file.write("Parsed successfully.\n")
        # Add actual parsing result saving logic here

# Run the application
root.mainloop()