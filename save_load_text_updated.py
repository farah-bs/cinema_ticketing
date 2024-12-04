import tkinter as tk
from tkinter import messagebox
import os

class CinemaSeating:
    def __init__(self, master, seating_plan):
        self.master = master
        self.seating_matrix = seating_plan  # Seating plan passed directly here
        self.rows = len(seating_plan)
        self.cols = max(len(row) for row in seating_plan)
        self.group_id = 1  # Start with group ID 1
        self.group_colors = self.load_group_colors()  # Load predefined colors
        self.create_gui()

    def load_group_colors(self):
        """Returns a dictionary of predefined group colors."""
        # A predefined list of 100 colors
        group_colors = {
            i: self.generate_color(i) for i in range(1, 101)
        }
        return group_colors

    def toggle_seat(self, row, col):
        """Toggles a seat's status between empty and assigned to the current group."""
        if self.seating_matrix[row][col] == 0:  # Empty seat
            if self.group_id not in self.group_colors:
                self.group_colors[self.group_id] = self.generate_color(self.group_id)

            self.seating_matrix[row][col] = self.group_id
            color = self.group_colors[self.group_id]
            self.seat_buttons[row][col].config(bg=color, text=f"G{self.group_id}")  # Show group ID
        elif self.seating_matrix[row][col] == self.group_id:  # Undo assignment
            self.seating_matrix[row][col] = 0
            seat_label = f"R{row + 1}C{col + 1}"  # Restore seat and row label
            self.seat_buttons[row][col].config(bg="white", text=seat_label)

    def create_gui(self):
        self.master.title("Cinema Seating")

        # Seat layout frame
        self.seat_frame = tk.Frame(self.master)
        self.seat_frame.pack(padx=10, pady=10)

        # Create seat buttons with seat and row numbers
        self.seat_buttons = []
        for r in range(self.rows):
            row_buttons = []
            for c in range(len(self.seating_matrix[r])):
                if self.seating_matrix[r][c] == 'x':
                    # Placeholder for non-existent seats
                    lbl = tk.Label(self.seat_frame, text=" ", width=5, height=1, bg="grey")
                    lbl.grid(row=r, column=c, padx=2, pady=2)
                    row_buttons.append(None)
                else:
                    seat_label = f"R{r + 1}C{c + 1}"  # Row and Column numbers (1-based indexing)
                    btn = tk.Button(self.seat_frame, text=seat_label, width=5, height=1, bg="white",
                                    command=lambda r=r, c=c: self.toggle_seat(r, c))
                    btn.grid(row=r, column=c, padx=2, pady=2)
                    row_buttons.append(btn)
            self.seat_buttons.append(row_buttons)

        # Controls frame
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=10)

        # Group ID label, entry, and button in a single row (row 0)
        self.group_label = tk.Label(self.control_frame, text="Current Group ID:")
        self.group_label.grid(row=0, column=0, padx=5, sticky="e")  # Align to the right of the cell

        self.group_entry = tk.Entry(self.control_frame, width=5)
        self.group_entry.insert(0, str(self.group_id))
        self.group_entry.grid(row=0, column=1, padx=5)

        tk.Button(self.control_frame, text="Set Group", command=self.set_group).grid(row=0, column=2, padx=5)

        # Buttons on the same row (row 2) for "Show Group List", "Save Seating", and "Load Seating"
        tk.Button(self.control_frame, text="Show Group List", command=self.show_group_list).grid(row=2, column=0, padx=5)
        tk.Button(self.control_frame, text="Save Seating", command=self.save_seating).grid(row=2, column=1, padx=5)
        tk.Button(self.control_frame, text="Load Seating", command=self.load_seating).grid(row=2, column=2, padx=5)


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

    def show_group_list(self):
        """Displays a new window with a list of groups and their assigned seats."""
        group_window = tk.Toplevel(self.master)
        group_window.title("Group Assignments")

        group_assignments = {}
        for r in range(self.rows):
            for c in range(len(self.seating_matrix[r])):
                group_id = self.seating_matrix[r][c]
                if group_id != 0 and group_id != 'x':
                    if group_id not in group_assignments:
                        group_assignments[group_id] = []
                    group_assignments[group_id].append(f"SIBMSR{r+1}S{c+1}")

        group_list_str = ""
        for group_id, seats in group_assignments.items():
            group_list_str += f"Group {group_id}: {', '.join(seats)}\n"

        if group_list_str:
            text_widget = tk.Text(group_window, wrap=tk.WORD, width=50, height=10)
            text_widget.insert(tk.END, group_list_str)
            text_widget.config(state=tk.DISABLED)
            text_widget.pack(padx=10, pady=10)
        else:
            group_label = tk.Label(group_window, text="No groups have been assigned yet.", justify=tk.LEFT)
            group_label.pack(padx=10, pady=10)

    def save_seating(self):
        """Saves the seating matrix to a text file."""
        try:
            with open("seating_plan.txt", "w") as file:
                for row in self.seating_matrix:
                    file.write(" ".join(str(seat) for seat in row) + "\n")
            messagebox.showinfo("Saved", "Seating plan has been saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save seating plan: {e}")

    def load_seating(self):
        """Loads the seating matrix from a text file."""
        try:
            if os.path.exists("seating_plan.txt"):
                with open("seating_plan.txt", "r") as file:
                    rows = file.readlines()
                    self.seating_matrix = [
                        [int(seat) if seat != 'x' else 'x' for seat in row.strip().split()]
                        for row in rows
                    ]
                self.update_seat_buttons()
                messagebox.showinfo("Loaded", "Seating plan has been loaded.")
            else:
                messagebox.showinfo("Info", "No saved seating plan found, using default.")
                self.seating_matrix = self.get_default_seating_plan()
                self.update_seat_buttons()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load seating plan: {e}")

    def update_seat_buttons(self):
        """Updates the seat buttons based on the current seating matrix."""
        for r in range(self.rows):
            for c in range(len(self.seating_matrix[r])):
                seat = self.seating_matrix[r][c]
                if seat == 0:
                    seat_label = f"R{r+1}C{c+1}"
                    if self.seat_buttons[r][c]:
                        self.seat_buttons[r][c].config(bg="white", text=seat_label)
                elif seat == 'x':
                    if self.seat_buttons[r][c]:
                        self.seat_buttons[r][c].config(bg="grey", text=" ")
                else:
                    color = self.group_colors.get(seat, "white")
                    if self.seat_buttons[r][c]:
                        self.seat_buttons[r][c].config(bg=color, text=f"G{seat}")

    def get_default_seating_plan(self):
        """Returns the default seating plan (empty seats)."""
        return [[0 for _ in range(self.cols)] for _ in range(self.rows)]

    @staticmethod
    def generate_color(group_id):
        """Generates a unique color for the given group."""
        import random
        random.seed(group_id)
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    import os
import shutil

def organize_pdfs_by_group(group_list, pdf_folder):
    """
    Organize PDFs into directories based on group names.

    Parameters:
        group_list (list): A list of group names.
        pdf_folder (str): The folder containing the PDF files to be organized.

    Returns:
        None
    """
    # Loop through each group in the group list
    for group in group_list:
        group_dir = os.path.join(pdf_folder, group)

        # Create directory for the group if it doesn't exist
        if not os.path.exists(group_dir):
            os.makedirs(group_dir)
            print(f"Directory created for group: {group}")

        # Loop through all PDF files in the pdf_folder
        for file_name in os.listdir(pdf_folder):
            # Check if the file is a PDF
            if file_name.endswith(".pdf"):
                # Assuming the PDF file name includes the group name
                if group in file_name:
                    # Define the source and destination file paths
                    source_file = os.path.join(pdf_folder, file_name)
                    destination_file = os.path.join(group_dir, file_name)

                    # Move the PDF file to the group's directory
                    shutil.move(source_file, destination_file)
                    print(f"Moved {file_name} to {group_dir}")


def main():
    root = tk.Tk()

    seating_plan = []
    # Try loading the seating plan from file
    if os.path.exists("seating_plan.txt"):
        with open("seating_plan.txt", "r") as file:
            seating_plan = [
                [int(seat) if seat != 'x' else 'x' for seat in row.strip().split()]
                for row in file.readlines()
            ]
    else:
        seating_plan = [[0 for _ in range(10)] for _ in range(10)]  # Default plan (10x10 grid)
    
    app = CinemaSeating(root, seating_plan)
    root.mainloop()

if __name__ == "__main__":
    main()
