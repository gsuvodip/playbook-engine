import os
from dotenv import load_dotenv
import threading

import tkinter as tk

from tkinter import ttk, messagebox, scrolledtext

from processor.playbook_processor import process_playbook, load_playbook

load_dotenv()  # Load environment variables from .env file

PLAYBOOK_PATH = os.getenv("PLAYBOOK_PATH")


class PlaybookAutomationGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Playbook Engine")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        # Dictionary to hold the dynamic checkbox BooleanVar objects
        self.checkbox_vars = {}

        title = ttk.Label(
            root,
            text="Playbook Engine",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        # --- Button Frame ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        self.load_btn = ttk.Button(
            btn_frame,
            text="Load Playbook",
            width=25,
            command=self.get_sheetnames  # Linked callback
        )
        self.load_btn.grid(row=0, column=0, padx=5)

        self.fetch_btn = ttk.Button(
            btn_frame,
            text="Fetch Data & Store Emails",
            width=25,
            command=self.fetch_data  # Linked callback
        )
        self.fetch_btn.grid(row=0, column=1, padx=5)

        self.exit_btn = ttk.Button(
            btn_frame,
            text="Exit",
            width=15,
            command=self.confirm_exit
        )
        self.exit_btn.grid(row=0, column=2, padx=5)

        # Main Paned Window
        main_paned = tk.PanedWindow(
            root,
            orient=tk.HORIZONTAL,
            sashrelief=tk.RAISED
        )
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- SCROLLABLE : Checkbox Panel (On Left) ---
        sidebar_frame = ttk.LabelFrame(main_paned, text="Select Sheets", padding=10)
        main_paned.add(sidebar_frame, width=200, minsize=150)

        # Create a Canvas and a Scrollbar inside the Sidebar Frame
        self.canvas = tk.Canvas(sidebar_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar_frame, orient="vertical", command=self.canvas.yview)

        # This frame lives inside the canvas and holds the actual checkboxes
        self.checkbox_frame = ttk.Frame(self.canvas)
        
        # Configure canvas window behavior
        self.canvas_window = self.canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        
        # Bind events to update scroll region when the internal frame size changes
        self.checkbox_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Layout canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Optional: Bind mousewheel scrolling to canvas
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # --- Right Panel (Table + Logs)
        right_paned = tk.PanedWindow(
            main_paned,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED
        )
        main_paned.add(right_paned, stretch="always")

        # --- Table Frame ---
        table_frame = ttk.Frame(right_paned)
        right_paned.add(table_frame, stretch="always")

        # Make frame expandable
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        table_label = ttk.Label(
            table_frame,
            text="Stored Draft Emails",
            font=("Segoe UI", 10, "bold")
        )

        table_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=(5, 5)
        )

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        # Table - Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Template", "Subject"),
            show="headings",
            selectmode="browse", # single selection only
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        self.tree.heading("ID", text="ID")
        self.tree.heading("Template", text="Template")
        self.tree.heading("Subject", text="Subject")

        self.tree.column("ID", width=100, stretch=False)
        self.tree.column("Template", width=200, stretch=False)
        self.tree.column("Subject", width=800, stretch=True)

        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        # --- Log Frame ---
        log_frame = ttk.Frame(right_paned)
        right_paned.add(log_frame, minsize=100)

        log_label = ttk.Label(
            log_frame,
            text="Execution Logs",
            font=("Segoe UI", 10, "bold")
        )
        log_label.pack(anchor="w", pady=(5, 5))

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            wrap=tk.WORD
        )
        self.log_area.config(state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Close Window Confirmation
        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)

    def log_message(self, message):
        """Helper function to safely log messages to the disabled text area."""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)  # Auto-scroll to bottom
        self.log_area.config(state=tk.DISABLED)

    def get_sheetnames(self):
        threading.Thread(
            target=self._get_sheetnames_worker,
            daemon=True
        ).start()

    def _get_sheetnames_worker(self):
        try:
            self.fetch_btn.config(state=tk.DISABLED)
            self.log_message(f"Loading playbook: {PLAYBOOK_PATH}")
            sheet_names = load_playbook(PLAYBOOK_PATH)

            self.root.after(0, self._populate_checkboxes, sheet_names)

            messagebox.showinfo(
                "Success",
                "Sheetnames fetched successfully."
            )
            
        except Exception as e:
            self.log_message(f"Error during playbook processing: {e}")
        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state=tk.ACTIVE))

    def _populate_checkboxes(self, sheet_names):
        """Clears old checkboxes and generates new ones based on returned sheets."""
        # Clear existing widgets inside the checkbox frame
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()
            
        self.checkbox_vars.clear()

        # Generate new checkboxes
        for idx, name in enumerate(sheet_names):
            var = tk.BooleanVar(value=False)  # Default to Unchecked
            self.checkbox_vars[name] = var
            
            cb = ttk.Checkbutton(
                self.checkbox_frame, 
                text=name, 
                variable=var,
                command=self.on_checkbox_toggle  # Event trigger if needed
            )
            cb.grid(row=idx, column=0, sticky="w", pady=3, padx=5)

    def on_checkbox_toggle(self):
        """Helper method to see which items are selected at any given time"""
        selected_sheets = [sheet for sheet, var in self.checkbox_vars.items() if var.get()]
        print(f"Currently selected sheets: {selected_sheets}")


    def fetch_data(self):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
    
        threading.Thread(
            target=self._fetch_data_worker,
            daemon=True
        ).start()

    def _fetch_data_worker(self):
        self.fetch_btn.config(state=tk.DISABLED)
        process_playbook(PLAYBOOK_PATH)

    def confirm_exit(self):
        result = messagebox.askyesno(
            "Confirm Exit",
            "Are you sure you want to exit the application?"
        )

        if result:
            self.root.destroy()


def main():
    root = tk.Tk()
    PlaybookAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
