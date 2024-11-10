import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv

# Global variables to store filenames and validation flags
production_filename = "No file loaded"
parse_table_filename = "No file loaded"
is_production_loaded = False
is_parsetable_loaded = False

productions_values = None
parse_table_values = None


def parse_tokens_with_grammar(productions: dict, parse_table: dict):
    """
    Parses tokens from the input field using a specified grammar.

    Args:
        productions (dict): Dictionary containing production rules.
        parse_table (dict): Dictionary representing the parse table.
    """
    input_tokens = tokens_entry.get().strip().split()
    if not input_tokens:
        messagebox.showerror("Error", "No input tokens provided!")
        return

    starting_production_rule = productions[0][1]  # 2nd column of 1st row

    stack = ["$", starting_production_rule]
    input_buffer = input_tokens + ["$"]
    parsing_steps = []
    is_valid = True

    while stack:
        stack_top = stack[-1]
        current_input = input_buffer[0]
        current_stack = " ".join(stack)
        current_buffer = " ".join(input_buffer)

        if stack_top == current_input:
            stack.pop()
            input_buffer.pop(0)
            action = f"Match {stack_top}"

        elif stack_top in parse_table:
            if current_input in parse_table[stack_top]:
                production_number = parse_table[stack_top][current_input]
                if production_number == "":
                    action = "Error: No rule found"
                    is_valid = False
                    break
                else:
                    stack.pop()
                    production = productions[int(production_number) - 1]
                    rhs = production[2].split() if production[2] != "e" else []
                    stack.extend(reversed(rhs))
                    action = f"Output {production[1]} -> {production[2]}"
            else:
                action = "Error: No matching terminal in parse table"
                is_valid = False
                break

        else:
            action = f"Error: Unexpected token {stack_top}"
            is_valid = False
            break

        parsing_steps.append((current_stack, current_buffer, action))

    # Display the parsing steps in the result table
    for row in parsing_result_table.get_children():
        parsing_result_table.delete(row)

    for step in parsing_steps:
        parsing_result_table.insert("", "end", values=step)

    # Save the parsing steps to an output file
    output_filename = get_output_filename()
    if output_filename:
        try:
            # Write parsing steps to the output file
            with open(output_filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Stack", "Input Buffer", "Action"])
                for step in parsing_steps:
                    writer.writerow(step)

            # After saving, update the parsing message label with the result and output filename
            if is_valid:
                parsing_message_label.config(
                    text=f"PARSING: Valid. Please see {output_filename}"
                )
            else:
                parsing_message_label.config(
                    text=f"PARSING: Invalid. Please see {output_filename}"
                )

            messagebox.showinfo("Success", f"Parsing steps saved to {output_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save parsing steps: {e}")


def load_productions(file_path):
    """
    Loads production rules from a .prod file.

    Args:
        file_path (str): Path to the production file.

    Returns:
        list: List of production rules.
    """
    productions = []
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            productions.append(row)
    return productions


def load_parse_table(file_path):
    """
    Loads parse table from a .ptbl file.

    Args:
        file_path (str): Path to the parse table file.

    Returns:
        dict: Dictionary representing the parse table.
    """
    parse_table = {}
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        headers = next(reader)[1:]
        for row in reader:
            non_terminal = row[0]
            parse_table[non_terminal] = {
                headers[i]: row[i + 1] for i in range(len(headers))
            }
    return parse_table


def load_file():
    """
    Opens a file dialog for loading production or parse table files.
    Updates the UI with the loaded file's content and enables parsing if both files are loaded.
    """
    global \
        production_filename, \
        parse_table_filename, \
        is_production_loaded, \
        is_parsetable_loaded
    global productions_values, parse_table_values

    file_path = filedialog.askopenfilename(
        filetypes=[("Production or Parse Table Files", "*.prod *.ptbl")]
    )
    if not file_path:
        return

    try:
        with open(file_path, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            file_content = list(reader)

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

            parsing_result_table.delete(*parsing_result_table.get_children())
            parsing_message_label.config(text="PARSING: Not yet parsed")

            if is_production_loaded and is_parsetable_loaded:
                parse_button.config(state=tk.NORMAL)

            loaded_file_label.config(text=f" {file_path.split('/')[-1]}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")


def display_content(table, content, columns):
    """
    Displays content in a Treeview table with fixed column width.

    Args:
        table (ttk.Treeview): The table to display content in.
        content (list): List of rows to be displayed in the table.
        columns (list): List of column names.
    """
    table["columns"] = columns
    for row in table.get_children():
        table.delete(row)

    fixed_width = 80
    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=fixed_width, stretch=tk.NO)

    for row in content:
        if len(row) == len(columns):
            table.insert("", "end", values=row)


def get_output_filename():
    """
    Asks the user for an output filename and appends the production filename.

    Returns:
        str or None: Path for saving parsed results, or None if cancelled.
    """
    return filedialog.asksaveasfilename(
        defaultextension=".prsd", filetypes=[("Parsed File", "*.prsd")]
    )


# Initialize the main Tkinter window
root = tk.Tk()
root.title("Non-Recursive Predictive Parser")
root.state("zoomed")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)

# UI Elements
production_frame = tk.LabelFrame(
    root, text="Productions", font=("Courier New", 12, "bold")
)
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
parse_table["columns"] = ["Non-Terminals"]

load_button = tk.Button(
    root,
    text="Load",
    command=load_file,
    font=("Courier New", 12, "bold"),
    bg="#20283E",
    fg="white",
)
load_button.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="nsew")

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

input_frame = tk.Frame(root)
input_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

tk.Label(input_frame, text="INPUT:", font=("Courier New", 12, "bold")).grid(
    row=0, column=0, padx=5, pady=5, sticky="w"
)

tokens_entry = tk.Entry(input_frame, font=("Courier New", 12), width=30)
tokens_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

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

root.mainloop()
