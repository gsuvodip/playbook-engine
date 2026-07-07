import tkinter as tk

from tkinter import ttk, messagebox, scrolledtext


class PlaybookAutomationGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Playbook Engine")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        title = ttk.Label(
            root,
            text="Playbook Engine",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        # --- Button Frame ---
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        self.fetch_btn = ttk.Button(
            btn_frame,
            text="Fetch Data & Store Emails",
            width=25,
            command=self.fetch_data  # Linked callback
        )
        self.fetch_btn.grid(row=0, column=0, padx=5)

        self.exit_btn = ttk.Button(
            btn_frame,
            text="Exit",
            width=15,
            command=self.confirm_exit
        )
        self.exit_btn.grid(row=0, column=2, padx=5)

        # Main Paned Window
        paned = tk.PanedWindow(
            root,
            orient=tk.VERTICAL,
            sashrelief=tk.RAISED
        )
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Table Frame ---
        table_frame = ttk.Frame(paned)
        paned.add(table_frame, stretch="always")

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

        # Episode Table - Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Episode", "Template", "Subject"),
            show="headings",
            selectmode="browse", # single selection only
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        self.tree.heading("Episode", text="Episode")
        self.tree.heading("Template", text="Template")
        self.tree.heading("Subject", text="Subject")

        self.tree.column("Episode", width=100, stretch=False)
        self.tree.column("Template", width=200, stretch=False)
        self.tree.column("Subject", width=800, stretch=True)

        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        hsb.grid(row=2, column=0, sticky="ew")

        # --- Log Frame ---
        log_frame = ttk.Frame(paned)
        paned.add(log_frame, minsize=100)

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

    def fetch_data(self):
        """Placeholder function for processing/fetching data."""
        self.log_message("Starting data fetch sequence...")
        # Your backend logic goes here
        messagebox.showinfo(
                "Success",
                "Email data stored successfully."
            )

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
