import customtkinter as ctk
import re
import os
from tkinter import messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

class DAEFixer(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.title("DAE Fixer")
        self.geometry("500x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Set custom icon
        icon_path = os.path.join(os.path.dirname(__file__), "cubes.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        else:
            print("Warning: Icon file 'cubes.ico' not found.")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.drop_area = ctk.CTkFrame(self, width=460, height=150)
        self.drop_area.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.drop_files)

        self.drop_label = ctk.CTkLabel(self.drop_area, text="Drag and Drop\ndae/DAE File(s) or Folder", 
                                       font=("Arial", 14), text_color="gray")
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=1, column=0, pady=(0, 10))
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.process_button = ctk.CTkButton(self.button_frame, text="Process", command=self.process_files, width=100)
        self.process_button.grid(row=0, column=0, padx=(0, 5))

        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", command=self.reset, 
                                          width=100, fg_color="#e74c3c", hover_color="#c0392b")
        self.reset_button.grid(row=0, column=1, padx=(5, 0))

        self.output_text = ctk.CTkTextbox(self, width=460, height=150)
        self.output_text.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self.progress_bar = ctk.CTkProgressBar(self, width=460)
        self.progress_bar.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)

        self.files_to_process = []

    def is_dae_file(self, filename):
        return filename.lower().endswith('.dae')

    def drop_files(self, event):
        files = self.tk.splitlist(event.data)
        self.files_to_process = []
        self.output_text.delete('1.0', ctk.END)
        for file in files:
            if os.path.isdir(file):
                for root, _, filenames in os.walk(file):
                    for filename in filenames:
                        if self.is_dae_file(filename):
                            full_path = os.path.join(root, filename)
                            self.files_to_process.append(full_path)
                            self.output_text.insert(ctk.END, f"Added: {full_path}\n")
            elif self.is_dae_file(file):
                self.files_to_process.append(file)
                self.output_text.insert(ctk.END, f"Added: {file}\n")
        
        if not self.files_to_process:
            messagebox.showwarning("No Valid Files", "No .dae/.DAE files were found in the dropped items.")
        else:
            self.output_text.insert(ctk.END, f"\nTotal files to process: {len(self.files_to_process)}\n")

    def process_files(self):
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please drag and drop .dae/.DAE file(s) or a folder containing .dae/.DAE files first.")
            return

        self.output_text.insert(ctk.END, "\nProcessing files...\n")
        self.progress_bar.set(0)
        
        total_files = len(self.files_to_process)
        output_folder = None

        if total_files > 1:
            output_folder = os.path.join(os.path.dirname(self.files_to_process[0]), "dae_fixed")
            os.makedirs(output_folder, exist_ok=True)

        for i, file in enumerate(self.files_to_process):
            self.process_file(file, output_folder)
            self.progress_bar.set((i + 1) / total_files)
            self.update_idletasks()
        
        self.output_text.insert(ctk.END, f"\nProcessed {total_files} file(s).\n")
        messagebox.showinfo("Process Complete", f"Successfully processed {total_files} file(s).")

    def process_file(self, input_file, output_folder=None):
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        if output_folder:
            output_file = os.path.join(output_folder, f"{base_name}_fixed.dae")
        else:
            output_file = os.path.join(os.path.dirname(input_file), f"{base_name}_fixed.dae")
        
        try:
            with open(input_file, 'r') as f:
                content = f.read()

            pattern = r'<texture[^>]*>.*?</texture>|<texture[^>]*\s*/>'
            
            def replace_texture(match):
                return ''

            cleaned_content = re.sub(pattern, replace_texture, content, flags=re.DOTALL)

            with open(output_file, 'w') as f:
                f.write(cleaned_content)

            self.output_text.insert(ctk.END, f"Processed: {input_file} -> {output_file}\n")
        except Exception as e:
            self.output_text.insert(ctk.END, f"Error processing {input_file}: {str(e)}\n")

    def reset(self):
        self.files_to_process = []
        self.output_text.delete('1.0', ctk.END)
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = DAEFixer()
    app.mainloop()
