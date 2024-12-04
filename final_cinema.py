import tkinter as tk
from tkinter import messagebox
import os

class CinemaSeatingFromText:
    def __init__(self, master, seat_file):
        self.master = master
        self.seat_file = seat_file
        self.group_id = 1  # Start with group ID 1
        self.group_colors = {}  # Initialize the group colors dictionary
        self.seating_matrix = self.load_seating_plan()  # Load the seating plan
        self.rows = len(self.seating_matrix)  # Number of rows
        self.cols = max(sum(int("&" in seat) + 1 for seat in seats) for seats in self.seating_matrix.values())
        self.seat_buttons = {}  # Dictionary to hold buttons
        self.buttons = []  # Initialize the buttons attribute as an empty list
        self.create_gui()

    def generate_color(self, group_id):
        """Generate a unique color for the group."""
        return f"#{(group_id * 1234567) % 0xFFFFFF:06x}"

    def load_seating_plan(self):
        """Reads the seat file and parses it into a seating matrix."""
        seating = {}
        with open(self.seat_file, 'r') as file:
            for line in file:
                row, seats = line.strip().split(",")
                if row not in seating:
                    seating[row] = []
                seating[row].extend(seats.split())
        return seating

    def toggle_seat_from_label(self, button):
        """
        Toggles a seat or sofa's state based on the button's label.
        :param button: The Tkinter button representing the seat/sofa.
        """
        label = button.cget("text")  # Get the label text from the button
        print(f"Toggling seat for label: {label}")

        # Parse the label to extract row and column(s)
        if "S" in label:  # Sofa case, e.g., R12S6-7 or R11S5 (single sofa seat)
            row_part, cols = label[1:].split("S")  # Remove the "R" and split by "S"
            row = int(row_part)  # No need to subtract 1 if seating_matrix uses 1-based indexing
            
            if "-" in cols:  # Sofa with a range, e.g., S6-7
                start_col, end_col = map(int, cols.split("-"))
                col_range = list(range(start_col - 1, end_col))  # Convert to 0-based column range
            else:  # Single sofa seat, e.g., S5
                col_range = [int(cols) - 1]  # Single column in a list
        else:  # Single seat case, e.g., R12S6
            row_part, col_part = label[1:].split("S")
            row = int(row_part)  # No need to subtract 1
            col_range = [int(col_part) - 1]  # Single column in a list

        # Debugging: print the entire seating_matrix and check the row
        print("Current seating_matrix:", self.seating_matrix)
        print(f"Row {row} contents: {self.seating_matrix.get(row, 'Row does not exist')}")

        # Check if the row exists in seating_matrix
        row_str = str(row)  # Ensure the row is a string
        if row_str not in self.seating_matrix:
            print(f"Row {row} does not exist in seating_matrix.")
            return  # Or handle this case accordingly

        # Check the current state of the seat(s)
        seat_status = all(self.seating_matrix[row][col] == 0 for col in col_range)

        if seat_status:  # Empty seats
            if self.group_id not in self.group_colors:
                self.group_colors[self.group_id] = self.generate_color(self.group_id)

            # Assign the group ID to all seats in the range
            for col in col_range:
                self.seating_matrix[row][col] = self.group_id

            color = self.group_colors[self.group_id]
            seat_label = f"G{self.group_id}"
            button.config(bg=color, text=seat_label)
        elif all(self.seating_matrix[row][col] == self.group_id for col in col_range):  # Undo assignment
            for col in col_range:
                self.seating_matrix[row][col] = 0

            # Reset the button label
            button.config(bg="white", text=label)





    def create_gui(self):
        """Creates the GUI with seat buttons."""
        self.master.title("Cinema Seating Plan")
        seat_frame = tk.Frame(self.master)
        seat_frame.pack(padx=10, pady=10)

        # Initialize buttons as an empty list
        self.buttons = []  # Initialize self.buttons here

        for row_num, seats in self.seating_matrix.items():
            row_idx = int(row_num) - 1  # Convert row to 0-based index

            # Ensure there's a list for the row in self.buttons
            while len(self.buttons) <= row_idx:  # Make sure the row index exists
                self.buttons.append([])  # Append an empty list for each row

            col_idx = 0  # Start at column 0 for each row
            for seat in seats:
                if "&" in seat:  # Sofa seats
                    start, end = map(int, seat.split("&"))
                    span = end - start + 1  # Number of columns spanned
                    seat_label = f"R{row_num}S{start}-{end}"
                    btn = tk.Button(seat_frame, text=seat_label, width=span * 5, height=2, bg="white")
                    btn.config(command=lambda b=btn: self.toggle_seat_from_label(b))
                    btn.grid(row=row_idx, column=col_idx, columnspan=span, padx=2, pady=2, sticky="ew")
                    self.buttons[row_idx].append(btn)  # Store the button reference in the current row
                    col_idx += span  # Move column index forward by span
                else:  # Single seat
                    seat_label = f"R{row_num}S{seat}"
                    btn = tk.Button(seat_frame, text=seat_label, width=5, height=2, bg="white")
                    btn.config(command=lambda b=btn: self.toggle_seat_from_label(b))
                    btn.grid(row=row_idx, column=col_idx, padx=2, pady=2)
                    self.buttons[row_idx].append(btn)  # Store the button reference in the current row
                    col_idx += 1  # Move column index forward by 1



    # Controls frame
            self.control_frame = tk.Frame(self.master)
            self.control_frame.pack(pady=10)

            # Group ID label, entry, and button in a single row (row 0)
            self.group_label = tk.Label(self.control_frame, text="Current Group ID:")
            self.group_label.grid(row=0, column=0, padx=5, sticky="e")  # Align to the right of the cell

            self.group_entry = tk.Entry(self.control_frame, width=5)
            self.group_entry.insert(0, str(self.group_id))
            self.group_entry.grid(row=0, column=1, padx=5)

            tk.Button(self.control_frame, text="Set Group").grid(row=0, column=2, padx=5)

            # Buttons on the same row (row 2) for "Show Group List", "Save Seating", and "Load Seating"
            tk.Button(self.control_frame, text="Show Group List").grid(row=2, column=0, padx=5)
            tk.Button(self.control_frame, text="Save Seating").grid(row=2, column=1, padx=5)
            tk.Button(self.control_frame, text="Load Seating").grid(row=2, column=2, padx=5)

    def set_group(self):
        """Sets the current group ID."""
        try:
            group_id = int(self.group_entry.get())
            if group_id > 0:
                self.group_id = group_id
                if group_id not in self.group_colors:
                    # Assign a new color for this group
                    self.group_colors[group_id] = self.generate_color(group_id)
            else:
                messagebox.showerror("Error", "Group ID must be positive.")
        except ValueError:
            messagebox.showerror("Error", "Invalid Group ID. Enter a number.")
            
# Usage
if __name__ == "__main__":
    # Path to the seating plan file
    seat_file = "src/data/data_seatz.txt"
    root = tk.Tk()
    app = CinemaSeatingFromText(root, seat_file)
    root.mainloop()
