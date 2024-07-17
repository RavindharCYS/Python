import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import webbrowser

class MySQLManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL Database Manager")
        self.username = ""
        self.password = ""
        self.connection = None

        self.create_widgets()

    def create_widgets(self):
        # Title Label (Left Side)
        title_label = tk.Label(self.root, text="MySQL Database Manager", font=("Helvetica", 18, "bold"))
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        # LinkedIn Badge (Top Right Corner)
        linkedin_button = tk.Button(self.root, text="LinkedIn", command=self.open_linkedin_profile, bg="blue", fg="white")
        linkedin_button.grid(row=0, column=2, padx=20, pady=20, sticky="e")

        # Username and Password Entry (Middle)
        username_label = tk.Label(self.root, text="MySQL Username:")
        username_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=1, column=1, padx=20, pady=5)

        password_label = tk.Label(self.root, text="MySQL Password:")
        password_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=2, column=1, padx=20, pady=5)

        connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        connect_button.grid(row=3, column=1, padx=20, pady=10, sticky="e")

        # Databases Listbox (Middle)
        databases_label = tk.Label(self.root, text="Available Databases:")
        databases_label.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.databases_listbox = tk.Listbox(self.root, height=10, width=50)
        self.databases_listbox.grid(row=5, column=0, rowspan=5, padx=20, pady=10, sticky="nsew")
        self.databases_listbox.bind("<<ListboxSelect>>", self.on_database_select)

        # Tables Listbox (Middle)
        tables_label = tk.Label(self.root, text="Available Tables:")
        tables_label.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        self.tables_listbox = tk.Listbox(self.root, height=10, width=50)
        self.tables_listbox.grid(row=5, column=1, rowspan=5, padx=20, pady=10, sticky="nsew")
        self.tables_listbox.bind("<<ListboxSelect>>", self.on_table_select)

        # Buttons for Table Interactions (Right Side)
        display_button = tk.Button(self.root, text="Display", command=self.display_table_contents)
        display_button.grid(row=1, column=2, padx=20, pady=5, sticky="w")

        add_button = tk.Button(self.root, text="Add", command=self.add_record)
        add_button.grid(row=2, column=2, padx=20, pady=5, sticky="w")

        modify_button = tk.Button(self.root, text="Modify", command=self.modify_record)
        modify_button.grid(row=3, column=2, padx=20, pady=5, sticky="w")

        # Text Area for Table Contents (Right Side)
        self.table_contents_text = tk.Text(self.root, height=10, width=70)
        self.table_contents_text.grid(row=4, column=2, rowspan=6, padx=20, pady=10, sticky="nsew")

    def connect_to_server(self):
        self.username = self.username_entry.get().strip()
        self.password = self.password_entry.get().strip()

        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user=self.username,
                password=self.password
            )
            if self.connection.is_connected():
                messagebox.showinfo("Success", "Connected to MySQL Server")
                self.update_databases_list()
        except Error as e:
            messagebox.showerror("Error", f"Error: {e}")

    def update_databases_list(self):
        self.databases_listbox.delete(0, tk.END)
        databases = self.list_databases()
        for db in databases:
            self.databases_listbox.insert(tk.END, db)

    def list_databases(self):
        cursor = self.connection.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        return [db[0] for db in databases]

    def on_database_select(self, event):
        if self.databases_listbox.curselection():
            selected_database = self.databases_listbox.get(self.databases_listbox.curselection())
            self.update_tables_list(selected_database)

    def update_tables_list(self, database):
        self.tables_listbox.delete(0, tk.END)
        tables = self.list_tables(database)
        for table in tables:
            self.tables_listbox.insert(tk.END, table)

    def list_tables(self, database):
        cursor = self.connection.cursor()
        cursor.execute(f"USE {database}")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        return [table[0] for table in tables]

    def on_table_select(self, event):
        pass  # No action needed on table select for now

    def display_table_contents(self, event=None):
        if self.tables_listbox.curselection():
            selected_table = self.tables_listbox.get(self.tables_listbox.curselection()[0])
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {selected_table}")
            rows = cursor.fetchall()
            cursor.close()

            self.table_contents_text.delete(1.0, tk.END)

            if not rows:
                self.table_contents_text.insert(tk.END, f"Table '{selected_table}' is empty.")
            else:
                columns = [col[0] for col in cursor.description]
                self.table_contents_text.insert(tk.END, ", ".join(columns) + "\n")
                for row in rows:
                    self.table_contents_text.insert(tk.END, ", ".join(str(col) for col in row) + "\n")

    def add_record(self, event=None):
        if self.tables_listbox.curselection():
            selected_table = self.tables_listbox.get(self.tables_listbox.curselection()[0])

            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {selected_table}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            values = []
            for col in column_names:
                value = simpledialog.askstring("Add Record", f"Enter value for {col}:")
                if value is None:
                    return  # User canceled
                values.append(value)

            values_str = "', '".join(values)
            insert_query = f"INSERT INTO {selected_table} VALUES ('{values_str}')"

            try:
                cursor.execute(insert_query)
                self.connection.commit()
                messagebox.showinfo("Success", "Record added successfully")
                self.display_table_contents()  # Refresh display after adding record
            except Error as e:
                messagebox.showerror("Error", f"Error adding record: {e}")

            cursor.close()

    def modify_record(self, event=None):
        if self.tables_listbox.curselection():
            selected_table = self.tables_listbox.get(self.tables_listbox.curselection()[0])

            pk_column = simpledialog.askstring("Modify Record", "Enter primary key column:")
            if pk_column is None:
                return  # User canceled

            pk_value = simpledialog.askstring("Modify Record", "Enter primary key value:")
            if pk_value is None:
                return  # User canceled

            # Prompt for new values for non-primary key columns
            new_values = {}
            cursor = self.connection.cursor()
            cursor.execute(f"DESCRIBE {selected_table}")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]

            for col in column_names:
                if col != pk_column:
                    value = simpledialog.askstring("Modify Record", f"Enter new value for {col} (leave blank to skip):")
                    if value is not None:
                        new_values[col] = value

            if not new_values:
                messagebox.showwarning("No Changes", "No changes were made.")
                return

            # Construct the UPDATE query
            set_clause = ", ".join(f"{col} = '{val}'" for col, val in new_values.items())
            update_query = f"UPDATE {selected_table} SET {set_clause} WHERE {pk_column} = '{pk_value}'"

            try:
                cursor.execute(update_query)
                self.connection.commit()
                messagebox.showinfo("Success", "Record modified successfully")
                self.display_table_contents()  # Refresh display after modifying record
            except Error as e:
                messagebox.showerror("Error", f"Error modifying record: {e}")

            cursor.close()

    def open_linkedin_profile(self):
        # Replace with your LinkedIn profile URL
        linkedin_url = "https://www.linkedin.com/in/ravindhar-cy/"

        # Open LinkedIn profile URL in the default web browser
        webbrowser.open_new_tab(linkedin_url)

def main():
    root = tk.Tk()
    app = MySQLManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

