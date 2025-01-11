import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from core.markdown_generator import  parse_gitignore, should_exclude, generate_markdown_with_excludes


class MarkdownGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Generator")

        # Dict to map node_id -> absolute path
        self.node_path_map = {}

        # Dict to track whether a node is checked
        self.node_checked_map = {}

        # Load icons here (once) so they are not garbage-collected
        icon_path_checked = os.path.join(os.path.dirname(__file__), "assets", "checkbox_checked.png")
        icon_path_unchecked = os.path.join(os.path.dirname(__file__), "assets", "checkbox_unchecked.png")
        print("Loading checked icon from:", icon_path_checked, icon_path_unchecked)
        self.checked_icon = tk.PhotoImage(file=icon_path_checked)
        self.unchecked_icon = tk.PhotoImage(file=icon_path_unchecked)

        self.create_widgets()

    def _should_exclude(self, path, exclude_patterns, root_dir):
        return should_exclude(path, exclude_patterns, root_dir)

    def on_item_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "tree":
            return  # Only toggle if they clicked in the "tree" region

        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Determine the current state and flip it
        current_state = self.node_checked_map[item_id]
        new_state = not current_state

        # Use our helper function to set item + sub-tree
        self.set_node_state(item_id, new_state)

    def get_checked_paths(self):
        checked = []
        for node_id, is_checked in self.node_checked_map.items():
            if is_checked:
                path = self.node_path_map[node_id]
                checked.append(path)
        return checked

    def get_unchecked_paths(self):
        unchecked = []
        for node_id, is_checked in self.node_checked_map.items():
            if not is_checked:
                unchecked.append(self.node_path_map[node_id])
        return unchecked

    def create_widgets(self):
        # Row 1: Label & Entry + 'Browse' button
        self.path_label = tk.Label(self.root, text="Project Directory:")
        self.path_label.pack(pady=5)

        self.path_entry = tk.Entry(self.root, width=50)
        self.path_entry.pack(pady=5)

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_directory)
        self.browse_button.pack(pady=5)

        # Row 2: Treeview Label
        self.preview_label = tk.Label(self.root, text="Project Structure Preview:")
        self.preview_label.pack(pady=(10, 0))

        # Row 3: A frame to contain the Treeview + scrollbar
        # NOTE the fill=tk.BOTH and expand=True here
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_scrollbar = tk.Scrollbar(tree_frame)
        self.tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, yscrollcommand=self.tree_scrollbar.set)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        # The Treeview also needs fill=tk.BOTH, expand=True
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_scrollbar.config(command=self.tree.yview)

        # Row 4: Generate Markdown Button + Status
        self.generate_button = tk.Button(self.root, text="Generate Markdown", command=self.generate_markdown)
        self.generate_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="", fg="green")
        self.status_label.pack(pady=5)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)

            # Populate the tree
            self.populate_treeview(directory)

    def generate_markdown(self):
        directory = self.path_entry.get()
        if not os.path.isdir(directory):
            messagebox.showerror("Error", "Invalid directory path!")
            return

        folder_name = os.path.basename(directory)
        default_file_name = f"{folder_name}.md"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md")],
            initialfile=default_file_name
        )
        if not save_path:
            return

        try:
            # 1) Gather the user’s unchecked paths
            user_excluded_paths = self.get_unchecked_paths()

            # 2) Call the new function that respects extra excludes
            generate_markdown_with_excludes(directory, save_path, user_excluded_paths)

            self.status_label.config(text=f"Markdown generated: {save_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    #### Helper functions ####

    def populate_treeview(self, directory):
        # 1. Clear any existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.node_path_map.clear()
        self.node_checked_map.clear()

        # 2. Parse .gitignore for exclude patterns
        exclude_patterns = parse_gitignore(directory)

        # 3. Insert root node for the selected directory
        #    CHANGED from unchecked_icon -> checked_icon
        root_node_id = self.tree.insert("", tk.END, text=os.path.basename(directory),
                                        image=self.checked_icon,
                                        open=True)
        # Also mark it as checked in our data structure
        self.node_path_map[root_node_id] = directory
        self.node_checked_map[root_node_id] = True

        # 4. Recursively add children
        self._add_children(root_node_id, directory, exclude_patterns)

    def _add_children(self, parent_node_id, directory, exclude_patterns):
        items = sorted(os.listdir(directory))
        for item in items:
            item_path = os.path.join(directory, item)
            if self._should_exclude(item_path, exclude_patterns, directory):
                continue

            if os.path.isdir(item_path):
                # Folder node -> use checked_icon & True as default
                folder_node_id = self.tree.insert(
                    parent_node_id,
                    tk.END,
                    text=item,
                    image=self.checked_icon,  # changed
                    open=False
                )
                self.node_path_map[folder_node_id] = item_path
                self.node_checked_map[folder_node_id] = True

                self._add_children(folder_node_id, item_path, exclude_patterns)
            else:
                # File node -> also checked by default
                file_node_id = self.tree.insert(
                    parent_node_id,
                    tk.END,
                    text=item,
                    image=self.checked_icon  # changed
                )
                self.node_path_map[file_node_id] = item_path
                self.node_checked_map[file_node_id] = True

    def set_node_state(self, item_id, new_state):
        """
        Recursively set the checked/unchecked state of 'item_id' and all its descendants.
        """
        # Update the current node
        self.node_checked_map[item_id] = new_state
        icon = self.checked_icon if new_state else self.unchecked_icon
        self.tree.item(item_id, image=icon)

        # Recursively update all children
        children = self.tree.get_children(item_id)
        for child_id in children:
            self.set_node_state(child_id, new_state)


if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownGeneratorApp(root)
    root.mainloop()
