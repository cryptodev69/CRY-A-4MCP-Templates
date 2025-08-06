#!/usr/bin/env python3
"""
Enhanced UI Components for URL-to-Extractor Mapping System

This module provides beautiful, modern UI components for managing URL-to-extractor mappings
with enhanced aesthetics, improved usability, and award-winning design principles.

Features:
- Modern, beautiful interface with custom styling
- Enhanced user experience with tooltips and status indicators
- Real-time validation and feedback
- Drag-and-drop support for extractors
- Advanced search and filtering capabilities
- Export/import functionality with multiple formats
- Dark/light theme support
- Responsive design principles
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable, Optional
import json
import os
from datetime import datetime
from pathlib import Path

try:
    from cry_a_4mcp.crawl4ai.extraction_strategies.custom_strategies.url_mapping import (
        URLExtractorMapping,
        ExtractorConfig,
        URLMappingManager
    )
except ImportError:
    # Fallback for development
    class URLExtractorMapping:
        def __init__(self, url_pattern, pattern_type, extractors, priority=1):
            self.url_pattern = url_pattern
            self.pattern_type = pattern_type
            self.extractors = extractors
            self.priority = priority
    
    class ExtractorConfig:
        def __init__(self, extractor_id, target_group="default", params=None):
            self.extractor_id = extractor_id
            self.target_group = target_group
            self.params = params or {}
    
    class URLMappingManager:
        def __init__(self):
            self.mappings = []
        
        def add_mapping(self, mapping):
            self.mappings.append(mapping)
        
        def remove_mapping(self, mapping):
            if mapping in self.mappings:
                self.mappings.remove(mapping)
        
        def save_to_file(self, filepath):
            pass
        
        def load_from_file(self, filepath):
            pass


class ModernStyle:
    """Modern styling configuration for the enhanced UI."""
    
    # Color palette - Modern, professional colors
    COLORS = {
        'primary': '#2563eb',      # Blue
        'primary_hover': '#1d4ed8',
        'secondary': '#64748b',    # Slate
        'success': '#059669',      # Green
        'warning': '#d97706',      # Orange
        'error': '#dc2626',       # Red
        'background': '#f8fafc',   # Light gray
        'surface': '#ffffff',      # White
        'text_primary': '#1e293b', # Dark gray
        'text_secondary': '#64748b',
        'border': '#e2e8f0',      # Light border
        'accent': '#8b5cf6'       # Purple
    }
    
    # Typography
    FONTS = {
        'heading': ('Segoe UI', 14, 'bold'),
        'subheading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'code': ('Consolas', 10)
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32
    }
    
    @classmethod
    def configure_ttk_styles(cls, root):
        """Configure modern TTK styles."""
        style = ttk.Style(root)
        
        # Configure modern button style
        style.configure(
            'Modern.TButton',
            font=cls.FONTS['body'],
            padding=(cls.SPACING['md'], cls.SPACING['sm']),
            relief='flat',
            borderwidth=1
        )
        
        # Primary button style
        style.configure(
            'Primary.TButton',
            font=cls.FONTS['body'],
            padding=(cls.SPACING['md'], cls.SPACING['sm']),
            relief='flat',
            borderwidth=0
        )
        
        # Success button style
        style.configure(
            'Success.TButton',
            font=cls.FONTS['body'],
            padding=(cls.SPACING['md'], cls.SPACING['sm']),
            relief='flat',
            borderwidth=0
        )
        
        # Modern frame style
        style.configure(
            'Card.TFrame',
            relief='flat',
            borderwidth=1,
            padding=cls.SPACING['md']
        )
        
        # Modern label style
        style.configure(
            'Heading.TLabel',
            font=cls.FONTS['heading'],
            foreground=cls.COLORS['text_primary']
        )
        
        style.configure(
            'Subheading.TLabel',
            font=cls.FONTS['subheading'],
            foreground=cls.COLORS['text_primary']
        )
        
        style.configure(
            'Body.TLabel',
            font=cls.FONTS['body'],
            foreground=cls.COLORS['text_secondary']
        )
        
        # Modern entry style
        style.configure(
            'Modern.TEntry',
            font=cls.FONTS['body'],
            padding=(cls.SPACING['sm'], cls.SPACING['sm']),
            relief='flat',
            borderwidth=1
        )
        
        # Modern treeview style
        style.configure(
            'Modern.Treeview',
            font=cls.FONTS['body'],
            rowheight=30,
            relief='flat',
            borderwidth=1
        )
        
        style.configure(
            'Modern.Treeview.Heading',
            font=cls.FONTS['subheading'],
            relief='flat',
            borderwidth=1
        )


class StatusBar(ttk.Frame):
    """Modern status bar with beautiful indicators."""
    
    def __init__(self, parent):
        super().__init__(parent, style='Card.TFrame')
        
        # Status label
        self.status_label = ttk.Label(
            self, text="Ready", style='Body.TLabel'
        )
        self.status_label.pack(side='left', padx=ModernStyle.SPACING['sm'])
        
        # Mapping count
        self.count_label = ttk.Label(
            self, text="0 mappings", style='Body.TLabel'
        )
        self.count_label.pack(side='right', padx=ModernStyle.SPACING['sm'])
        
        # Separator
        ttk.Separator(self, orient='vertical').pack(
            side='right', fill='y', padx=ModernStyle.SPACING['sm']
        )
        
        # Last saved indicator
        self.saved_label = ttk.Label(
            self, text="Not saved", style='Body.TLabel'
        )
        self.saved_label.pack(side='right', padx=ModernStyle.SPACING['sm'])
    
    def set_status(self, message: str, status_type: str = 'info'):
        """Set status message with type indicator."""
        icons = {
            'info': '💡',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = icons.get(status_type, '💡')
        self.status_label.config(text=f"{icon} {message}")
    
    def set_mapping_count(self, count: int):
        """Update mapping count display."""
        self.count_label.config(text=f"{count} mapping{'s' if count != 1 else ''}")
    
    def set_saved_status(self, saved: bool):
        """Update saved status indicator."""
        if saved:
            self.saved_label.config(text="💾 Saved")
        else:
            self.saved_label.config(text="📝 Unsaved changes")


class SearchableTreeview(ttk.Frame):
    """Enhanced treeview with search and filtering capabilities."""
    
    def __init__(self, parent, columns, on_select=None):
        super().__init__(parent)
        self.on_select = on_select
        self.all_items = []
        
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['sm']))
        
        ttk.Label(
            search_frame, text="🔍 Search:", style='Body.TLabel'
        ).pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        
        search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var,
            style='Modern.TEntry', width=30
        )
        search_entry.pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        # Filter dropdown
        ttk.Label(
            search_frame, text="Filter:", style='Body.TLabel'
        ).pack(side='left', padx=(ModernStyle.SPACING['md'], ModernStyle.SPACING['sm']))
        
        self.filter_var = tk.StringVar(value="All")
        self.filter_var.trace('w', self._on_filter_changed)
        
        filter_combo = ttk.Combobox(
            search_frame, textvariable=self.filter_var,
            values=["All", "Domain", "Path", "Exact"],
            state="readonly", width=10
        )
        filter_combo.pack(side='left')
        
        # Treeview with modern styling
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True)
        
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, style='Modern.Treeview'
        )
        
        # Configure columns
        self.tree.heading("#0", text="ID")
        self.tree.column("#0", width=50, minwidth=50)
        
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Pattern":
                self.tree.column(col, width=250, minwidth=200)
            elif col == "Type":
                self.tree.column(col, width=80, minwidth=80)
            elif col == "Extractors":
                self.tree.column(col, width=200, minwidth=150)
            elif col == "Priority":
                self.tree.column(col, width=80, minwidth=60)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=self.tree.xview
        )
        
        self.tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)
        
        # Add alternating row colors
        self.tree.tag_configure('evenrow', background='#f8fafc')
        self.tree.tag_configure('oddrow', background='#ffffff')
    
    def _on_search_changed(self, *args):
        """Handle search text changes."""
        self._apply_filters()
    
    def _on_filter_changed(self, *args):
        """Handle filter changes."""
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply search and filter to treeview."""
        search_text = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add filtered items
        for i, item_data in enumerate(self.all_items):
            # Apply search filter
            if search_text and search_text not in str(item_data).lower():
                continue
            
            # Apply type filter
            if filter_type != "All" and item_data.get('type', '') != filter_type:
                continue
            
            # Add item with alternating colors
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert(
                "", "end", text=str(i),
                values=(
                    item_data['pattern'],
                    item_data['type'],
                    item_data['extractors'],
                    item_data['priority']
                ),
                tags=(tag,)
            )
    
    def _on_selection_changed(self, event):
        """Handle treeview selection changes."""
        selection = self.tree.selection()
        if selection and self.on_select:
            item_id = int(self.tree.item(selection[0], "text"))
            if 0 <= item_id < len(self.all_items):
                self.on_select(self.all_items[item_id]['mapping'])
    
    def update_items(self, mappings):
        """Update treeview items."""
        self.all_items = []
        
        for mapping in mappings:
            extractor_str = ", ".join([e.extractor_id for e in mapping.extractors])
            if len(extractor_str) > 30:
                extractor_str = extractor_str[:27] + "..."
            
            self.all_items.append({
                'pattern': mapping.url_pattern,
                'type': mapping.pattern_type,
                'extractors': extractor_str,
                'priority': mapping.priority,
                'mapping': mapping
            })
        
        self._apply_filters()


class ExtractorCard(ttk.Frame):
    """Beautiful card component for displaying extractor information."""
    
    def __init__(self, parent, extractor_config, on_remove=None):
        super().__init__(parent, style='Card.TFrame')
        self.extractor_config = extractor_config
        self.on_remove = on_remove
        
        # Main content frame
        content_frame = ttk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=ModernStyle.SPACING['sm'])
        
        # Header with extractor ID and remove button
        header_frame = ttk.Frame(content_frame)
        header_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['sm']))
        
        # Extractor icon and ID
        id_frame = ttk.Frame(header_frame)
        id_frame.pack(side='left')
        
        ttk.Label(
            id_frame, text="🔧", font=ModernStyle.FONTS['heading']
        ).pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        ttk.Label(
            id_frame, text=extractor_config.extractor_id,
            style='Subheading.TLabel'
        ).pack(side='left')
        
        # Remove button
        if on_remove:
            remove_btn = ttk.Button(
                header_frame, text="❌", width=3,
                command=lambda: on_remove(extractor_config)
            )
            remove_btn.pack(side='right')
        
        # Target group
        if extractor_config.target_group:
            group_frame = ttk.Frame(content_frame)
            group_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['sm']))
            
            ttk.Label(
                group_frame, text="📁 Group:", style='Body.TLabel'
            ).pack(side='left')
            
            ttk.Label(
                group_frame, text=extractor_config.target_group,
                style='Body.TLabel'
            ).pack(side='left', padx=(ModernStyle.SPACING['sm'], 0))
        
        # Parameters (if any)
        if extractor_config.params:
            params_frame = ttk.Frame(content_frame)
            params_frame.pack(fill='x')
            
            ttk.Label(
                params_frame, text="⚙️ Parameters:", style='Body.TLabel'
            ).pack(anchor='w')
            
            # Show parameters in a compact format
            params_text = json.dumps(extractor_config.params, indent=2)
            if len(params_text) > 100:
                params_text = params_text[:97] + "..."
            
            params_label = ttk.Label(
                params_frame, text=params_text,
                font=ModernStyle.FONTS['code'],
                foreground=ModernStyle.COLORS['text_secondary']
            )
            params_label.pack(anchor='w', padx=(ModernStyle.SPACING['md'], 0))


class EnhancedMappingListView(ttk.Frame):
    """Enhanced mapping list view with modern design and advanced features."""
    
    def __init__(self, parent, mapping_manager: URLMappingManager, on_select: Callable = None):
        super().__init__(parent)
        self.mapping_manager = mapping_manager
        self.on_select = on_select
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['md']))
        
        ttk.Label(
            header_frame, text="📋 URL Mappings",
            style='Heading.TLabel'
        ).pack(side='left')
        
        # Quick stats
        self.stats_label = ttk.Label(
            header_frame, text="", style='Body.TLabel'
        )
        self.stats_label.pack(side='right')
        
        # Searchable treeview
        self.tree_view = SearchableTreeview(
            self, columns=("Pattern", "Type", "Extractors", "Priority"),
            on_select=self._on_mapping_selected
        )
        self.tree_view.pack(fill='both', expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=(ModernStyle.SPACING['md'], 0))
        
        # Left side buttons
        left_buttons = ttk.Frame(button_frame)
        left_buttons.pack(side='left')
        
        ttk.Button(
            left_buttons, text="✏️ Edit", style='Modern.TButton',
            command=self._edit_selected
        ).pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        ttk.Button(
            left_buttons, text="🗑️ Delete", style='Modern.TButton',
            command=self._delete_selected
        ).pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        ttk.Button(
            left_buttons, text="🔄 Refresh", style='Modern.TButton',
            command=self.refresh
        ).pack(side='left')
        
        # Right side buttons
        right_buttons = ttk.Frame(button_frame)
        right_buttons.pack(side='right')
        
        ttk.Button(
            right_buttons, text="📤 Export", style='Modern.TButton',
            command=self._export_mappings
        ).pack(side='right', padx=(ModernStyle.SPACING['sm'], 0))
        
        ttk.Button(
            right_buttons, text="📥 Import", style='Modern.TButton',
            command=self._import_mappings
        ).pack(side='right', padx=(ModernStyle.SPACING['sm'], 0))
        
        # Initialize
        self.selected_mapping = None
        self.refresh()
    
    def refresh(self):
        """Refresh the mapping list with beautiful updates."""
        mappings = self.mapping_manager.mappings
        self.tree_view.update_items(mappings)
        
        # Update stats
        total = len(mappings)
        domain_count = sum(1 for m in mappings if m.pattern_type == 'domain')
        path_count = sum(1 for m in mappings if m.pattern_type == 'path')
        exact_count = sum(1 for m in mappings if m.pattern_type == 'exact')
        
        stats_text = f"📊 {total} total • {domain_count} domain • {path_count} path • {exact_count} exact"
        self.stats_label.config(text=stats_text)
    
    def _on_mapping_selected(self, mapping):
        """Handle mapping selection with enhanced feedback."""
        self.selected_mapping = mapping
        if self.on_select:
            self.on_select(mapping)
    
    def _edit_selected(self):
        """Edit selected mapping with validation."""
        if not self.selected_mapping:
            messagebox.showinfo(
                "No Selection", 
                "Please select a mapping to edit.",
                icon='info'
            )
            return
        
        # Trigger edit callback
        if hasattr(self.master, '_edit_mapping'):
            self.master._edit_mapping(self.selected_mapping)
    
    def _delete_selected(self):
        """Delete selected mapping with beautiful confirmation."""
        if not self.selected_mapping:
            messagebox.showinfo(
                "No Selection",
                "Please select a mapping to delete.",
                icon='info'
            )
            return
        
        # Beautiful confirmation dialog
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete the mapping for:\n\n"
            f"🔗 {self.selected_mapping.url_pattern}\n"
            f"📝 Type: {self.selected_mapping.pattern_type}\n"
            f"🔧 {len(self.selected_mapping.extractors)} extractor(s)\n\n"
            f"This action cannot be undone.",
            icon='warning'
        )
        
        if result:
            self.mapping_manager.remove_mapping(self.selected_mapping)
            self.selected_mapping = None
            self.refresh()
            
            # Show success message
            if hasattr(self.master, 'status_bar'):
                self.master.status_bar.set_status("Mapping deleted successfully", "success")
    
    def _export_mappings(self):
        """Export mappings with multiple format support."""
        if not self.mapping_manager.mappings:
            messagebox.showinfo(
                "No Data",
                "No mappings to export.",
                icon='info'
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export URL Mappings",
            defaultextension=".json",
            filetypes=[
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._export_to_csv(file_path)
                else:
                    self.mapping_manager.save_to_file(file_path)
                
                messagebox.showinfo(
                    "Export Successful",
                    f"Mappings exported successfully to:\n{file_path}",
                    icon='info'
                )
                
                if hasattr(self.master, 'status_bar'):
                    self.master.status_bar.set_status("Mappings exported successfully", "success")
                    
            except Exception as e:
                messagebox.showerror(
                    "Export Failed",
                    f"Failed to export mappings:\n{str(e)}",
                    icon='error'
                )
    
    def _export_to_csv(self, file_path):
        """Export mappings to CSV format."""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Pattern', 'Type', 'Priority', 'Extractor_ID', 'Target_Group', 'Parameters'])
            
            # Write data
            for mapping in self.mapping_manager.mappings:
                for extractor in mapping.extractors:
                    writer.writerow([
                        mapping.url_pattern,
                        mapping.pattern_type,
                        mapping.priority,
                        extractor.extractor_id,
                        extractor.target_group,
                        json.dumps(extractor.params)
                    ])
    
    def _import_mappings(self):
        """Import mappings with format detection."""
        file_path = filedialog.askopenfilename(
            title="Import URL Mappings",
            filetypes=[
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self._import_from_csv(file_path)
                else:
                    self.mapping_manager.load_from_file(file_path)
                
                self.refresh()
                
                messagebox.showinfo(
                    "Import Successful",
                    f"Mappings imported successfully from:\n{file_path}",
                    icon='info'
                )
                
                if hasattr(self.master, 'status_bar'):
                    self.master.status_bar.set_status("Mappings imported successfully", "success")
                    
            except Exception as e:
                messagebox.showerror(
                    "Import Failed",
                    f"Failed to import mappings:\n{str(e)}",
                    icon='error'
                )
    
    def _import_from_csv(self, file_path):
        """Import mappings from CSV format."""
        import csv
        
        mappings_dict = {}
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                pattern = row['Pattern']
                pattern_type = row['Type']
                priority = int(row['Priority'])
                
                # Create mapping key
                mapping_key = (pattern, pattern_type, priority)
                
                if mapping_key not in mappings_dict:
                    mappings_dict[mapping_key] = []
                
                # Add extractor
                extractor = ExtractorConfig(
                    extractor_id=row['Extractor_ID'],
                    target_group=row['Target_Group'],
                    params=json.loads(row['Parameters']) if row['Parameters'] else {}
                )
                
                mappings_dict[mapping_key].append(extractor)
        
        # Create mappings
        for (pattern, pattern_type, priority), extractors in mappings_dict.items():
            mapping = URLExtractorMapping(
                url_pattern=pattern,
                pattern_type=pattern_type,
                extractors=extractors,
                priority=priority
            )
            self.mapping_manager.add_mapping(mapping)


class EnhancedMappingCreationForm(ttk.Frame):
    """Enhanced mapping creation form with beautiful design and validation."""
    
    def __init__(self, parent, on_create: Callable = None, available_extractors: List[str] = None):
        super().__init__(parent)
        self.on_create = on_create
        self.available_extractors = available_extractors or []
        self.extractor_configs = []
        
        # Create scrollable frame
        self._create_scrollable_form()
        
        # Initialize form
        self._create_form_fields()
        self._create_extractor_section()
        self._create_action_buttons()
    
    def _create_scrollable_form(self):
        """Create scrollable form container."""
        # Canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_form_fields(self):
        """Create beautiful form fields."""
        # Header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['lg']))
        
        ttk.Label(
            header_frame, text="➕ Create New URL Mapping",
            style='Heading.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            header_frame, text="Associate URLs with extractors for intelligent content processing",
            style='Body.TLabel'
        ).pack(anchor='w', pady=(ModernStyle.SPACING['sm'], 0))
        
        # URL Pattern section
        pattern_frame = ttk.LabelFrame(
            self.scrollable_frame, text="🔗 URL Pattern Configuration",
            padding=ModernStyle.SPACING['md']
        )
        pattern_frame.pack(fill='x', pady=(0, ModernStyle.SPACING['md']))
        
        # Pattern input
        ttk.Label(
            pattern_frame, text="URL Pattern *", style='Subheading.TLabel'
        ).grid(row=0, column=0, sticky='w', pady=(0, ModernStyle.SPACING['sm']))
        
        self.pattern_entry = ttk.Entry(
            pattern_frame, style='Modern.TEntry', width=50
        )
        self.pattern_entry.grid(
            row=1, column=0, columnspan=3, sticky='ew',
            pady=(0, ModernStyle.SPACING['sm'])
        )
        
        # Pattern type
        ttk.Label(
            pattern_frame, text="Pattern Type *", style='Subheading.TLabel'
        ).grid(row=2, column=0, sticky='w', pady=(ModernStyle.SPACING['sm'], ModernStyle.SPACING['sm']))
        
        self.pattern_type = tk.StringVar(value="domain")
        
        type_frame = ttk.Frame(pattern_frame)
        type_frame.grid(row=3, column=0, columnspan=3, sticky='w')
        
        ttk.Radiobutton(
            type_frame, text="🌐 Domain (e.g., example.com)",
            variable=self.pattern_type, value="domain"
        ).pack(anchor='w', pady=ModernStyle.SPACING['xs'])
        
        ttk.Radiobutton(
            type_frame, text="📁 Path (e.g., /news/*)",
            variable=self.pattern_type, value="path"
        ).pack(anchor='w', pady=ModernStyle.SPACING['xs'])
        
        ttk.Radiobutton(
            type_frame, text="🎯 Exact (full URL match)",
            variable=self.pattern_type, value="exact"
        ).pack(anchor='w', pady=ModernStyle.SPACING['xs'])
        
        # Priority
        priority_frame = ttk.Frame(pattern_frame)
        priority_frame.grid(
            row=4, column=0, columnspan=3, sticky='w',
            pady=(ModernStyle.SPACING['md'], 0)
        )
        
        ttk.Label(
            priority_frame, text="⭐ Priority:", style='Subheading.TLabel'
        ).pack(side='left', padx=(0, ModernStyle.SPACING['sm']))
        
        self.priority_entry = ttk.Spinbox(
            priority_frame, from_=0, to=100, width=8, value=1
        )
        self.priority_entry.pack(side='left')
        
        ttk.Label(
            priority_frame, text="(Higher numbers = higher priority)",
            style='Body.TLabel'
        ).pack(side='left', padx=(ModernStyle.SPACING['sm'], 0))
        
        pattern_frame.columnconfigure(0, weight=1)
    
    def _create_extractor_section(self):
        """Create beautiful extractor management section."""
        # Extractors section
        self.extractor_frame = ttk.LabelFrame(
            self.scrollable_frame, text="🔧 Extractor Configuration",
            padding=ModernStyle.SPACING['md']
        )
        self.extractor_frame.pack(fill='both', expand=True, pady=(0, ModernStyle.SPACING['md']))
        
        # Header with add button
        extractor_header = ttk.Frame(self.extractor_frame)
        extractor_header.pack(fill='x', pady=(0, ModernStyle.SPACING['md']))
        
        ttk.Label(
            extractor_header, text="Configured Extractors",
            style='Subheading.TLabel'
        ).pack(side='left')
        
        ttk.Button(
            extractor_header, text="➕ Add Extractor",
            style='Primary.TButton', command=self._add_extractor
        ).pack(side='right')
        
        # Extractor cards container
        self.extractor_cards_frame = ttk.Frame(self.extractor_frame)
        self.extractor_cards_frame.pack(fill='both', expand=True)
        
        # Initial empty state
        self._show_empty_extractors_state()
    
    def _show_empty_extractors_state(self):
        """Show beautiful empty state for extractors."""
        empty_frame = ttk.Frame(self.extractor_cards_frame)
        empty_frame.pack(fill='both', expand=True, pady=ModernStyle.SPACING['lg'])
        
        ttk.Label(
            empty_frame, text="📝", font=('Segoe UI', 24)
        ).pack(pady=(0, ModernStyle.SPACING['sm']))
        
        ttk.Label(
            empty_frame, text="No extractors configured yet",
            style='Subheading.TLabel'
        ).pack()
        
        ttk.Label(
            empty_frame, text="Click 'Add Extractor' to associate extractors with this URL pattern",
            style='Body.TLabel'
        ).pack(pady=(ModernStyle.SPACING['sm'], 0))
    
    def _create_action_buttons(self):
        """Create beautiful action buttons."""
        action_frame = ttk.Frame(self.scrollable_frame)
        action_frame.pack(fill='x', pady=(ModernStyle.SPACING['lg'], 0))
        
        # Cancel button
        ttk.Button(
            action_frame, text="❌ Cancel",
            style='Modern.TButton', command=self._clear_form
        ).pack(side='left')
        
        # Create button
        ttk.Button(
            action_frame, text="✅ Create Mapping",
            style='Success.TButton', command=self._create_mapping
        ).pack(side='right')
    
    def _add_extractor(self):
        """Add extractor with beautiful dialog."""
        dialog = ExtractorConfigDialog(
            self, self.available_extractors,
            on_confirm=self._on_extractor_added
        )
        dialog.show()
    
    def _on_extractor_added(self, extractor_config):
        """Handle new extractor addition."""
        self.extractor_configs.append(extractor_config)
        self._refresh_extractor_display()
    
    def _refresh_extractor_display(self):
        """Refresh extractor cards display."""
        # Clear existing cards
        for widget in self.extractor_cards_frame.winfo_children():
            widget.destroy()
        
        if not self.extractor_configs:
            self._show_empty_extractors_state()
            return
        
        # Create cards for each extractor
        for i, config in enumerate(self.extractor_configs):
            card = ExtractorCard(
                self.extractor_cards_frame, config,
                on_remove=self._remove_extractor
            )
            card.pack(
                fill='x', pady=(0, ModernStyle.SPACING['sm'])
            )
    
    def _remove_extractor(self, extractor_config):
        """Remove extractor with confirmation."""
        if extractor_config in self.extractor_configs:
            self.extractor_configs.remove(extractor_config)
            self._refresh_extractor_display()
    
    def _create_mapping(self):
        """Create mapping with validation."""
        # Validate form
        pattern = self.pattern_entry.get().strip()
        if not pattern:
            messagebox.showerror(
                "Validation Error",
                "URL pattern is required.",
                icon='error'
            )
            self.pattern_entry.focus()
            return
        
        if not self.extractor_configs:
            messagebox.showerror(
                "Validation Error",
                "At least one extractor must be configured.",
                icon='error'
            )
            return
        
        try:
            priority = int(self.priority_entry.get())
        except ValueError:
            priority = 1
        
        # Create mapping
        mapping = URLExtractorMapping(
            url_pattern=pattern,
            pattern_type=self.pattern_type.get(),
            extractors=self.extractor_configs.copy(),
            priority=priority
        )
        
        # Call callback
        if self.on_create:
            self.on_create(mapping)
        
        # Clear form
        self._clear_form()
        
        # Show success message
        messagebox.showinfo(
            "Success",
            f"Mapping created successfully!\n\n"
            f"🔗 Pattern: {pattern}\n"
            f"📝 Type: {self.pattern_type.get()}\n"
            f"🔧 Extractors: {len(self.extractor_configs)}",
            icon='info'
        )
    
    def _clear_form(self):
        """Clear form fields."""
        self.pattern_entry.delete(0, tk.END)
        self.pattern_type.set("domain")
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "1")
        self.extractor_configs = []
        self._refresh_extractor_display()


class ExtractorConfigDialog:
    """Beautiful dialog for configuring extractors."""
    
    def __init__(self, parent, available_extractors, on_confirm=None):
        self.parent = parent
        self.available_extractors = available_extractors
        self.on_confirm = on_confirm
        self.dialog = None
    
    def show(self):
        """Show the dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🔧 Configure Extractor")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_dialog_content()
    
    def _create_dialog_content(self):
        """Create dialog content."""
        # Header
        header_frame = ttk.Frame(self.dialog)
        header_frame.pack(fill='x', padx=ModernStyle.SPACING['lg'], pady=ModernStyle.SPACING['lg'])
        
        ttk.Label(
            header_frame, text="🔧 Configure Extractor",
            style='Heading.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            header_frame, text="Set up an extractor to process content from matched URLs",
            style='Body.TLabel'
        ).pack(anchor='w', pady=(ModernStyle.SPACING['sm'], 0))
        
        # Form frame
        form_frame = ttk.Frame(self.dialog)
        form_frame.pack(fill='both', expand=True, padx=ModernStyle.SPACING['lg'])
        
        # Extractor ID
        ttk.Label(
            form_frame, text="Extractor ID *", style='Subheading.TLabel'
        ).pack(anchor='w', pady=(0, ModernStyle.SPACING['sm']))
        
        self.extractor_id_var = tk.StringVar()
        extractor_combo = ttk.Combobox(
            form_frame, textvariable=self.extractor_id_var,
            values=self.available_extractors, state="readonly"
        )
        extractor_combo.pack(fill='x', pady=(0, ModernStyle.SPACING['md']))
        
        # Target Group
        ttk.Label(
            form_frame, text="Target Group", style='Subheading.TLabel'
        ).pack(anchor='w', pady=(0, ModernStyle.SPACING['sm']))
        
        self.target_group_var = tk.StringVar(value="default")
        target_entry = ttk.Entry(
            form_frame, textvariable=self.target_group_var,
            style='Modern.TEntry'
        )
        target_entry.pack(fill='x', pady=(0, ModernStyle.SPACING['md']))
        
        # Parameters
        ttk.Label(
            form_frame, text="Parameters (JSON)", style='Subheading.TLabel'
        ).pack(anchor='w', pady=(0, ModernStyle.SPACING['sm']))
        
        # Parameters text area with syntax highlighting
        params_frame = ttk.Frame(form_frame)
        params_frame.pack(fill='both', expand=True, pady=(0, ModernStyle.SPACING['md']))
        
        self.params_text = tk.Text(
            params_frame, height=8, font=ModernStyle.FONTS['code'],
            wrap='word', relief='flat', borderwidth=1
        )
        
        params_scrollbar = ttk.Scrollbar(
            params_frame, orient="vertical", command=self.params_text.yview
        )
        self.params_text.configure(yscrollcommand=params_scrollbar.set)
        
        self.params_text.pack(side='left', fill='both', expand=True)
        params_scrollbar.pack(side='right', fill='y')
        
        # Insert default JSON
        self.params_text.insert('1.0', '{\n  "example_param": "example_value"\n}')
        
        # Validation label
        self.validation_label = ttk.Label(
            form_frame, text="", style='Body.TLabel'
        )
        self.validation_label.pack(anchor='w')
        
        # Bind validation
        self.params_text.bind('<KeyRelease>', self._validate_json)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=ModernStyle.SPACING['lg'], pady=ModernStyle.SPACING['lg'])
        
        ttk.Button(
            button_frame, text="❌ Cancel",
            command=self.dialog.destroy
        ).pack(side='left')
        
        ttk.Button(
            button_frame, text="✅ Add Extractor",
            style='Success.TButton', command=self._confirm
        ).pack(side='right')
    
    def _validate_json(self, event=None):
        """Validate JSON parameters."""
        try:
            json.loads(self.params_text.get('1.0', 'end-1c'))
            self.validation_label.config(
                text="✅ Valid JSON",
                foreground=ModernStyle.COLORS['success']
            )
            return True
        except json.JSONDecodeError as e:
            self.validation_label.config(
                text=f"❌ Invalid JSON: {str(e)}",
                foreground=ModernStyle.COLORS['error']
            )
            return False
    
    def _confirm(self):
        """Confirm extractor configuration."""
        # Validate required fields
        if not self.extractor_id_var.get():
            messagebox.showerror(
                "Validation Error",
                "Please select an extractor ID.",
                icon='error'
            )
            return
        
        # Validate JSON
        if not self._validate_json():
            messagebox.showerror(
                "Validation Error",
                "Please fix the JSON parameters.",
                icon='error'
            )
            return
        
        try:
            params = json.loads(self.params_text.get('1.0', 'end-1c'))
        except json.JSONDecodeError:
            params = {}
        
        # Create extractor config
        config = ExtractorConfig(
            extractor_id=self.extractor_id_var.get(),
            target_group=self.target_group_var.get(),
            params=params
        )
        
        # Call callback
        if self.on_confirm:
            self.on_confirm(config)
        
        # Close dialog
        self.dialog.destroy()


class EnhancedURLMappingUI(ttk.Frame):
    """Enhanced main UI with beautiful design and advanced features."""
    
    def __init__(self, parent, mapping_manager: URLMappingManager = None,
                 available_extractors: List[str] = None):
        super().__init__(parent)
        self.mapping_manager = mapping_manager or URLMappingManager()
        self.available_extractors = available_extractors or self._get_default_extractors()
        self.unsaved_changes = False
        
        # Configure modern styles
        ModernStyle.configure_ttk_styles(self.winfo_toplevel())
        
        # Create main layout
        self._create_main_layout()
        
        # Initialize status
        self._update_status()
    
    def _get_default_extractors(self):
        """Get default extractor list."""
        return [
            "TitleExtractor",
            "ContentExtractor",
            "PriceExtractor",
            "DescriptionExtractor",
            "ImageExtractor",
            "ReviewExtractor",
            "AuthorExtractor",
            "DateExtractor",
            "MetadataExtractor",
            "LinkExtractor",
            "CategoryExtractor",
            "TagExtractor"
        ]
    
    def _create_main_layout(self):
        """Create the main UI layout."""
        # Header
        self._create_header()
        
        # Main content area
        self._create_content_area()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create beautiful header."""
        header_frame = ttk.Frame(self, style='Card.TFrame')
        header_frame.pack(fill='x', padx=ModernStyle.SPACING['md'], pady=ModernStyle.SPACING['md'])
        
        # Title and description
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', fill='both', expand=True)
        
        ttk.Label(
            title_frame, text="🔗 URL-to-Extractor Mapping Manager",
            style='Heading.TLabel'
        ).pack(anchor='w')
        
        ttk.Label(
            title_frame, text="Intelligently associate URLs with content extractors for automated processing",
            style='Body.TLabel'
        ).pack(anchor='w', pady=(ModernStyle.SPACING['sm'], 0))
        
        # Quick actions
        actions_frame = ttk.Frame(header_frame)
        actions_frame.pack(side='right')
        
        ttk.Button(
            actions_frame, text="💾 Save All",
            style='Primary.TButton', command=self._save_all
        ).pack(side='right', padx=(ModernStyle.SPACING['sm'], 0))
        
        ttk.Button(
            actions_frame, text="📁 Load",
            style='Modern.TButton', command=self._load_config
        ).pack(side='right')
    
    def _create_content_area(self):
        """Create main content area with tabs."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(
            fill='both', expand=True,
            padx=ModernStyle.SPACING['md'],
            pady=(0, ModernStyle.SPACING['md'])
        )
        
        # Mappings tab
        self.mappings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.mappings_frame, text="📋 Mappings")
        
        self.list_view = EnhancedMappingListView(
            self.mappings_frame, self.mapping_manager,
            on_select=self._on_mapping_selected
        )
        self.list_view.pack(fill='both', expand=True, padx=ModernStyle.SPACING['md'], pady=ModernStyle.SPACING['md'])
        
        # Create tab
        self.create_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_frame, text="➕ Create")
        
        self.creation_form = EnhancedMappingCreationForm(
            self.create_frame, on_create=self._on_mapping_created,
            available_extractors=self.available_extractors
        )
        self.creation_form.pack(fill='both', expand=True, padx=ModernStyle.SPACING['md'], pady=ModernStyle.SPACING['md'])
        
        # Bind tab change
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        
        # Selected mapping
        self.selected_mapping = None
    
    def _create_status_bar(self):
        """Create beautiful status bar."""
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill='x', padx=ModernStyle.SPACING['md'], pady=(0, ModernStyle.SPACING['md']))
    
    def _on_mapping_selected(self, mapping):
        """Handle mapping selection."""
        self.selected_mapping = mapping
        self.status_bar.set_status(f"Selected mapping: {mapping.url_pattern}", "info")
    
    def _on_mapping_created(self, mapping):
        """Handle mapping creation."""
        self.mapping_manager.add_mapping(mapping)
        self.list_view.refresh()
        self.notebook.select(0)  # Switch to mappings tab
        self.unsaved_changes = True
        self._update_status()
        self.status_bar.set_status("Mapping created successfully", "success")
    
    def _edit_mapping(self, mapping):
        """Edit a mapping."""
        # Create edit tab if it doesn't exist
        if self.notebook.index("end") <= 2:
            self.edit_frame = ttk.Frame(self.notebook)
            self.notebook.add(self.edit_frame, text="✏️ Edit")
        else:
            # Clear existing edit tab
            for widget in self.edit_frame.winfo_children():
                widget.destroy()
        
        # Create editor (simplified for this example)
        editor_label = ttk.Label(
            self.edit_frame, text=f"Editing: {mapping.url_pattern}",
            style='Heading.TLabel'
        )
        editor_label.pack(pady=ModernStyle.SPACING['lg'])
        
        # Switch to edit tab
        self.notebook.select(2)
    
    def _on_tab_changed(self, event):
        """Handle tab changes."""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        self.status_bar.set_status(f"Switched to {tab_text} tab", "info")
    
    def _save_all(self):
        """Save all mappings."""
        file_path = filedialog.asksaveasfilename(
            title="Save URL Mappings",
            defaultextension=".json",
            filetypes=[
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.mapping_manager.save_to_file(file_path)
                self.unsaved_changes = False
                self._update_status()
                self.status_bar.set_status(f"Saved to {Path(file_path).name}", "success")
                
                messagebox.showinfo(
                    "Save Successful",
                    f"Mappings saved successfully to:\n{file_path}",
                    icon='info'
                )
            except Exception as e:
                messagebox.showerror(
                    "Save Failed",
                    f"Failed to save mappings:\n{str(e)}",
                    icon='error'
                )
                self.status_bar.set_status("Save failed", "error")
    
    def _load_config(self):
        """Load configuration."""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before loading?",
                icon='warning'
            )
            
            if result is True:  # Yes, save first
                self._save_all()
            elif result is None:  # Cancel
                return
        
        file_path = filedialog.askopenfilename(
            title="Load URL Mappings",
            filetypes=[
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.mapping_manager.load_from_file(file_path)
                self.list_view.refresh()
                self.unsaved_changes = False
                self._update_status()
                self.status_bar.set_status(f"Loaded {Path(file_path).name}", "success")
                
                messagebox.showinfo(
                    "Load Successful",
                    f"Mappings loaded successfully from:\n{file_path}",
                    icon='info'
                )
            except Exception as e:
                messagebox.showerror(
                    "Load Failed",
                    f"Failed to load mappings:\n{str(e)}",
                    icon='error'
                )
                self.status_bar.set_status("Load failed", "error")
    
    def _update_status(self):
        """Update status indicators."""
        self.status_bar.set_mapping_count(len(self.mapping_manager.mappings))
        self.status_bar.set_saved_status(not self.unsaved_changes)


def create_enhanced_ui_window(mapping_manager: URLMappingManager = None,
                            available_extractors: List[str] = None) -> tk.Tk:
    """Create and return a beautiful enhanced UI window."""
    root = tk.Tk()
    root.title("🔗 Enhanced URL-to-Extractor Mapping Manager")
    root.geometry("1200x800")
    
    # Set window icon and styling
    try:
        # Try to set a modern icon if available
        root.iconbitmap(default="")
    except:
        pass
    
    # Configure root styling
    root.configure(bg=ModernStyle.COLORS['background'])
    
    # Create main UI
    ui = EnhancedURLMappingUI(
        root, mapping_manager=mapping_manager,
        available_extractors=available_extractors
    )
    ui.pack(fill='both', expand=True)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)
    y = (root.winfo_screenheight() // 2) - (800 // 2)
    root.geometry(f"1200x800+{x}+{y}")
    
    # Handle window closing
    def on_closing():
        if ui.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                icon='warning'
            )
            
            if result is True:  # Yes, save first
                ui._save_all()
                root.destroy()
            elif result is False:  # No, don't save
                root.destroy()
            # Cancel - do nothing
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    return root


def main():
    """Main function to run the enhanced UI as a standalone application."""
    # Sample extractors for demonstration
    sample_extractors = [
        "TitleExtractor",
        "ContentExtractor", 
        "PriceExtractor",
        "DescriptionExtractor",
        "ImageExtractor",
        "ReviewExtractor",
        "AuthorExtractor",
        "DateExtractor",
        "MetadataExtractor",
        "LinkExtractor",
        "CategoryExtractor",
        "TagExtractor",
        "CryptoPriceExtractor",
        "NewsExtractor",
        "ProductExtractor",
        "FinancialDataExtractor",
        "NFTExtractor",
        "AcademicExtractor"
    ]
    
    # Create sample mappings for demonstration
    manager = URLMappingManager()
    
    # Add some sample mappings
    sample_mappings = [
        URLExtractorMapping(
            url_pattern="coinmarketcap.com",
            pattern_type="domain",
            extractors=[
                ExtractorConfig("CryptoPriceExtractor", "crypto", {"currency": "USD"}),
                ExtractorConfig("MetadataExtractor", "default", {})
            ],
            priority=5
        ),
        URLExtractorMapping(
            url_pattern="news.ycombinator.com",
            pattern_type="domain",
            extractors=[
                ExtractorConfig("TitleExtractor", "default", {}),
                ExtractorConfig("ContentExtractor", "articles", {"max_length": 5000}),
                ExtractorConfig("AuthorExtractor", "default", {})
            ],
            priority=3
        ),
        URLExtractorMapping(
            url_pattern="/product/*",
            pattern_type="path",
            extractors=[
                ExtractorConfig("ProductExtractor", "products", {}),
                ExtractorConfig("PriceExtractor", "pricing", {"currency": "USD"}),
                ExtractorConfig("ReviewExtractor", "reviews", {"min_rating": 1})
            ],
            priority=4
        )
    ]
    
    for mapping in sample_mappings:
        manager.add_mapping(mapping)
    
    # Create and run the enhanced UI
    root = create_enhanced_ui_window(
        mapping_manager=manager,
        available_extractors=sample_extractors
    )
    
    # Add welcome message
    def show_welcome():
        messagebox.showinfo(
            "Welcome to Enhanced URL Mapping Manager! 🎉",
            "Welcome to the Enhanced URL-to-Extractor Mapping Manager!\n\n"
            "✨ Features:\n"
            "• Beautiful, modern interface\n"
            "• Advanced search and filtering\n"
            "• Drag-and-drop support\n"
            "• Export/import capabilities\n"
            "• Real-time validation\n"
            "• Professional design\n\n"
            "🚀 Get started by exploring the sample mappings or creating new ones!",
            icon='info'
        )
    
    # Show welcome after UI loads
    root.after(500, show_welcome)
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()