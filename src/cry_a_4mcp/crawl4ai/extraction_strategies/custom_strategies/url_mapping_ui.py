#!/usr/bin/env python3
"""
UI Components for URL-to-Extractor Mapping System

This module provides UI components for managing URL-to-extractor mappings,
including views for listing, creating, editing, and deleting mappings.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable, Optional

from cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_mapping import (
    URLExtractorMapping,
    ExtractorConfig,
    URLMappingManager
)


class MappingListView(ttk.Frame):
    """UI component for displaying a list of URL mappings."""
    
    def __init__(self, parent, mapping_manager: URLMappingManager, on_select: Callable = None):
        """Initialize the mapping list view.
        
        Args:
            parent: Parent widget.
            mapping_manager: The URL mapping manager to display mappings from.
            on_select: Callback function to call when a mapping is selected.
        """
        super().__init__(parent)
        self.mapping_manager = mapping_manager
        self.on_select = on_select
        
        # Create treeview for displaying mappings
        self.tree = ttk.Treeview(self, columns=("Pattern", "Type", "Extractors", "Priority"))
        self.tree.heading("#0", text="ID")
        self.tree.heading("Pattern", text="URL Pattern")
        self.tree.heading("Type", text="Pattern Type")
        self.tree.heading("Extractors", text="Extractors")
        self.tree.heading("Priority", text="Priority")
        
        self.tree.column("#0", width=50)
        self.tree.column("Pattern", width=200)
        self.tree.column("Type", width=100)
        self.tree.column("Extractors", width=200)
        self.tree.column("Priority", width=50)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_mapping_selected)
        
        # Refresh the list
        self.refresh()
    
    def refresh(self):
        """Refresh the mapping list."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add mappings to the tree
        for i, mapping in enumerate(self.mapping_manager.mappings):
            extractor_str = ", ".join([e.extractor_id for e in mapping.extractors])
            self.tree.insert(
                "", "end", text=str(i),
                values=(
                    mapping.url_pattern,
                    mapping.pattern_type,
                    extractor_str,
                    mapping.priority
                )
            )
    
    def _on_mapping_selected(self, event):
        """Handle mapping selection event."""
        selection = self.tree.selection()
        if selection and self.on_select:
            item_id = int(self.tree.item(selection[0], "text"))
            if 0 <= item_id < len(self.mapping_manager.mappings):
                self.on_select(self.mapping_manager.mappings[item_id])


class MappingCreationForm(ttk.Frame):
    """UI component for creating a new URL mapping."""
    
    def __init__(self, parent, on_create: Callable = None, available_extractors: List[str] = None):
        """Initialize the mapping creation form.
        
        Args:
            parent: Parent widget.
            on_create: Callback function to call when a mapping is created.
            available_extractors: List of available extractor IDs.
        """
        super().__init__(parent)
        self.on_create = on_create
        self.available_extractors = available_extractors or []
        self.extractor_configs = []
        
        # Create form fields
        ttk.Label(self, text="URL Pattern:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pattern_entry = ttk.Entry(self, width=40)
        self.pattern_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self, text="Pattern Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pattern_type = tk.StringVar(value="domain")
        ttk.Radiobutton(self, text="Domain", variable=self.pattern_type, value="domain").grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )
        ttk.Radiobutton(self, text="Path", variable=self.pattern_type, value="path").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Radiobutton(self, text="Exact", variable=self.pattern_type, value="exact").grid(
            row=1, column=3, sticky="w", padx=5, pady=5
        )
        
        ttk.Label(self, text="Priority:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.priority_entry = ttk.Spinbox(self, from_=0, to=100, width=5)
        self.priority_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Extractors section
        ttk.Label(self, text="Extractors:", font=("TkDefaultFont", 10, "bold")).grid(
            row=3, column=0, columnspan=4, sticky="w", padx=5, pady=(15, 5)
        )
        
        # Extractor list
        self.extractor_frame = ttk.Frame(self)
        self.extractor_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        # Add extractor button
        ttk.Button(self, text="Add Extractor", command=self._add_extractor).grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        
        # Create button
        ttk.Button(self, text="Create Mapping", command=self._create_mapping).grid(
            row=6, column=0, columnspan=4, sticky="e", padx=5, pady=15
        )
    
    def _add_extractor(self):
        """Add a new extractor configuration."""
        # Create a dialog for adding an extractor
        dialog = tk.Toplevel(self)
        dialog.title("Add Extractor")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Extractor ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        extractor_id = ttk.Combobox(dialog, values=self.available_extractors)
        extractor_id.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(dialog, text="Target Group:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        target_group = ttk.Entry(dialog)
        target_group.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(dialog, text="Parameters (JSON):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        params = tk.Text(dialog, height=5, width=30)
        params.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        params.insert("1.0", "{}")
        
        def add():
            try:
                import json
                params_dict = json.loads(params.get("1.0", "end-1c"))
                
                config = ExtractorConfig(
                    extractor_id=extractor_id.get(),
                    target_group=target_group.get(),
                    params=params_dict
                )
                
                self.extractor_configs.append(config)
                self._refresh_extractor_list()
                dialog.destroy()
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON in parameters field")
        
        ttk.Button(dialog, text="Add", command=add).grid(
            row=3, column=0, columnspan=2, sticky="e", padx=5, pady=15
        )
    
    def _refresh_extractor_list(self):
        """Refresh the extractor list display."""
        # Clear existing widgets
        for widget in self.extractor_frame.winfo_children():
            widget.destroy()
        
        # Add headers
        ttk.Label(self.extractor_frame, text="ID", width=20).grid(row=0, column=0, sticky="w")
        ttk.Label(self.extractor_frame, text="Target Group", width=15).grid(row=0, column=1, sticky="w")
        ttk.Label(self.extractor_frame, text="Actions", width=10).grid(row=0, column=2, sticky="w")
        
        # Add extractors
        for i, config in enumerate(self.extractor_configs):
            ttk.Label(self.extractor_frame, text=config.extractor_id).grid(
                row=i+1, column=0, sticky="w", padx=5, pady=2
            )
            ttk.Label(self.extractor_frame, text=config.target_group).grid(
                row=i+1, column=1, sticky="w", padx=5, pady=2
            )
            
            # Remove button
            ttk.Button(
                self.extractor_frame, text="Remove",
                command=lambda idx=i: self._remove_extractor(idx)
            ).grid(row=i+1, column=2, sticky="w", padx=5, pady=2)
    
    def _remove_extractor(self, index):
        """Remove an extractor configuration.
        
        Args:
            index: Index of the extractor to remove.
        """
        if 0 <= index < len(self.extractor_configs):
            del self.extractor_configs[index]
            self._refresh_extractor_list()
    
    def _create_mapping(self):
        """Create a new mapping from the form data."""
        pattern = self.pattern_entry.get().strip()
        pattern_type = self.pattern_type.get()
        
        try:
            priority = int(self.priority_entry.get())
        except ValueError:
            priority = 0
        
        if not pattern:
            messagebox.showerror("Error", "URL pattern cannot be empty")
            return
        
        if not self.extractor_configs:
            messagebox.showerror("Error", "At least one extractor must be added")
            return
        
        # Create the mapping
        mapping = URLExtractorMapping(
            url_pattern=pattern,
            pattern_type=pattern_type,
            extractors=self.extractor_configs,
            priority=priority
        )
        
        # Call the callback
        if self.on_create:
            self.on_create(mapping)
        
        # Clear the form
        self.pattern_entry.delete(0, tk.END)
        self.pattern_type.set("domain")
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "0")
        self.extractor_configs = []
        self._refresh_extractor_list()


class MappingEditor(ttk.Frame):
    """UI component for editing an existing URL mapping."""
    
    def __init__(self, parent, mapping: URLExtractorMapping, on_save: Callable = None,
                 available_extractors: List[str] = None):
        """Initialize the mapping editor.
        
        Args:
            parent: Parent widget.
            mapping: The mapping to edit.
            on_save: Callback function to call when the mapping is saved.
            available_extractors: List of available extractor IDs.
        """
        super().__init__(parent)
        self.mapping = mapping
        self.on_save = on_save
        self.available_extractors = available_extractors or []
        self.extractor_configs = [ExtractorConfig(
            extractor_id=e.extractor_id,
            target_group=e.target_group,
            params=e.params
        ) for e in mapping.extractors]
        
        # Create form fields
        ttk.Label(self, text="URL Pattern:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.pattern_entry = ttk.Entry(self, width=40)
        self.pattern_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.pattern_entry.insert(0, mapping.url_pattern)
        
        ttk.Label(self, text="Pattern Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pattern_type = tk.StringVar(value=mapping.pattern_type)
        ttk.Radiobutton(self, text="Domain", variable=self.pattern_type, value="domain").grid(
            row=1, column=1, sticky="w", padx=5, pady=5
        )
        ttk.Radiobutton(self, text="Path", variable=self.pattern_type, value="path").grid(
            row=1, column=2, sticky="w", padx=5, pady=5
        )
        ttk.Radiobutton(self, text="Exact", variable=self.pattern_type, value="exact").grid(
            row=1, column=3, sticky="w", padx=5, pady=5
        )
        
        ttk.Label(self, text="Priority:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.priority_entry = ttk.Spinbox(self, from_=0, to=100, width=5)
        self.priority_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.priority_entry.insert(0, str(mapping.priority))
        
        # Extractors section
        ttk.Label(self, text="Extractors:", font=("TkDefaultFont", 10, "bold")).grid(
            row=3, column=0, columnspan=4, sticky="w", padx=5, pady=(15, 5)
        )
        
        # Extractor list
        self.extractor_frame = ttk.Frame(self)
        self.extractor_frame.grid(row=4, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        self._refresh_extractor_list()
        
        # Add extractor button
        ttk.Button(self, text="Add Extractor", command=self._add_extractor).grid(
            row=5, column=0, sticky="w", padx=5, pady=5
        )
        
        # Save button
        ttk.Button(self, text="Save Changes", command=self._save_mapping).grid(
            row=6, column=0, columnspan=4, sticky="e", padx=5, pady=15
        )
    
    def _add_extractor(self):
        """Add a new extractor configuration."""
        # Create a dialog for adding an extractor
        dialog = tk.Toplevel(self)
        dialog.title("Add Extractor")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Extractor ID:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        extractor_id = ttk.Combobox(dialog, values=self.available_extractors)
        extractor_id.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(dialog, text="Target Group:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        target_group = ttk.Entry(dialog)
        target_group.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(dialog, text="Parameters (JSON):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        params = tk.Text(dialog, height=5, width=30)
        params.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        params.insert("1.0", "{}")
        
        def add():
            try:
                import json
                params_dict = json.loads(params.get("1.0", "end-1c"))
                
                config = ExtractorConfig(
                    extractor_id=extractor_id.get(),
                    target_group=target_group.get(),
                    params=params_dict
                )
                
                self.extractor_configs.append(config)
                self._refresh_extractor_list()
                dialog.destroy()
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON in parameters field")
        
        ttk.Button(dialog, text="Add", command=add).grid(
            row=3, column=0, columnspan=2, sticky="e", padx=5, pady=15
        )
    
    def _refresh_extractor_list(self):
        """Refresh the extractor list display."""
        # Clear existing widgets
        for widget in self.extractor_frame.winfo_children():
            widget.destroy()
        
        # Add headers
        ttk.Label(self.extractor_frame, text="ID", width=20).grid(row=0, column=0, sticky="w")
        ttk.Label(self.extractor_frame, text="Target Group", width=15).grid(row=0, column=1, sticky="w")
        ttk.Label(self.extractor_frame, text="Actions", width=10).grid(row=0, column=2, sticky="w")
        
        # Add extractors
        for i, config in enumerate(self.extractor_configs):
            ttk.Label(self.extractor_frame, text=config.extractor_id).grid(
                row=i+1, column=0, sticky="w", padx=5, pady=2
            )
            ttk.Label(self.extractor_frame, text=config.target_group).grid(
                row=i+1, column=1, sticky="w", padx=5, pady=2
            )
            
            # Remove button
            ttk.Button(
                self.extractor_frame, text="Remove",
                command=lambda idx=i: self._remove_extractor(idx)
            ).grid(row=i+1, column=2, sticky="w", padx=5, pady=2)
    
    def _remove_extractor(self, index):
        """Remove an extractor configuration.
        
        Args:
            index: Index of the extractor to remove.
        """
        if 0 <= index < len(self.extractor_configs):
            del self.extractor_configs[index]
            self._refresh_extractor_list()
    
    def _save_mapping(self):
        """Save changes to the mapping."""
        pattern = self.pattern_entry.get().strip()
        pattern_type = self.pattern_type.get()
        
        try:
            priority = int(self.priority_entry.get())
        except ValueError:
            priority = 0
        
        if not pattern:
            messagebox.showerror("Error", "URL pattern cannot be empty")
            return
        
        if not self.extractor_configs:
            messagebox.showerror("Error", "At least one extractor must be added")
            return
        
        # Update the mapping
        self.mapping.url_pattern = pattern
        self.mapping.pattern_type = pattern_type
        self.mapping.priority = priority
        self.mapping.extractors = self.extractor_configs
        
        # Call the callback
        if self.on_save:
            self.on_save(self.mapping)


class URLMappingUI(ttk.Frame):
    """Main UI component for managing URL-to-extractor mappings."""
    
    def __init__(self, parent, mapping_manager: URLMappingManager = None,
                 available_extractors: List[str] = None):
        """Initialize the URL mapping UI.
        
        Args:
            parent: Parent widget.
            mapping_manager: The URL mapping manager to use.
            available_extractors: List of available extractor IDs.
        """
        super().__init__(parent)
        self.mapping_manager = mapping_manager or URLMappingManager()
        self.available_extractors = available_extractors or []
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.list_frame = ttk.Frame(self.notebook)
        self.create_frame = ttk.Frame(self.notebook)
        self.edit_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.list_frame, text="Mappings")
        self.notebook.add(self.create_frame, text="Create")
        
        # Create mapping list view
        self.list_view = MappingListView(
            self.list_frame, self.mapping_manager, on_select=self._on_mapping_selected
        )
        self.list_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add buttons for list view
        button_frame = ttk.Frame(self.list_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Edit", command=self._edit_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Delete", command=self._delete_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Refresh", command=self._refresh_list).pack(side="left", padx=5)
        
        # Add save/load buttons
        ttk.Button(button_frame, text="Save Config", command=self._save_config).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Load Config", command=self._load_config).pack(side="right", padx=5)
        
        # Create mapping creation form
        self.creation_form = MappingCreationForm(
            self.create_frame, on_create=self._on_mapping_created,
            available_extractors=self.available_extractors
        )
        self.creation_form.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Selected mapping
        self.selected_mapping = None
    
    def _on_mapping_selected(self, mapping):
        """Handle mapping selection.
        
        Args:
            mapping: The selected mapping.
        """
        self.selected_mapping = mapping
    
    def _on_mapping_created(self, mapping):
        """Handle mapping creation.
        
        Args:
            mapping: The created mapping.
        """
        self.mapping_manager.add_mapping(mapping)
        self._refresh_list()
        self.notebook.select(0)  # Switch to list tab
    
    def _on_mapping_saved(self, mapping):
        """Handle mapping save.
        
        Args:
            mapping: The saved mapping.
        """
        self._refresh_list()
        self.notebook.select(0)  # Switch to list tab
        
        # Remove the edit tab
        if self.notebook.index("end") > 2:
            self.notebook.forget(2)
    
    def _edit_selected(self):
        """Edit the selected mapping."""
        if not self.selected_mapping:
            messagebox.showinfo("Info", "Please select a mapping to edit")
            return
        
        # Remove existing edit tab if it exists
        if self.notebook.index("end") > 2:
            self.notebook.forget(2)
        
        # Create new edit tab
        self.edit_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.edit_frame, text="Edit")
        
        # Create editor
        editor = MappingEditor(
            self.edit_frame, self.selected_mapping, on_save=self._on_mapping_saved,
            available_extractors=self.available_extractors
        )
        editor.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Switch to edit tab
        self.notebook.select(2)
    
    def _delete_selected(self):
        """Delete the selected mapping."""
        if not self.selected_mapping:
            messagebox.showinfo("Info", "Please select a mapping to delete")
            return
        
        # Confirm deletion
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this mapping?"):
            self.mapping_manager.remove_mapping(self.selected_mapping)
            self.selected_mapping = None
            self._refresh_list()
    
    def _refresh_list(self):
        """Refresh the mapping list."""
        self.list_view.refresh()
    
    def _save_config(self):
        """Save the current configuration to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.mapping_manager.save_config(file_path)
                messagebox.showinfo("Success", "Configuration saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def _load_config(self):
        """Load configuration from a file."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                self.mapping_manager.load_config(file_path)
                self._refresh_list()
                messagebox.showinfo("Success", "Configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")


def main():
    """Run the URL mapping UI as a standalone application."""
    root = tk.Tk()
    root.title("URL-to-Extractor Mapping Manager")
    root.geometry("800x600")
    
    # Sample available extractors
    available_extractors = [
        "PriceExtractor",
        "DescriptionExtractor",
        "TitleExtractor",
        "ImageExtractor",
        "ReviewExtractor",
        "AuthorExtractor",
        "DateExtractor",
        "ContentExtractor"
    ]
    
    # Create mapping manager
    mapping_manager = URLMappingManager()
    
    # Create UI
    ui = URLMappingUI(root, mapping_manager, available_extractors)
    ui.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()